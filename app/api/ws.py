"""
WebSocket endpoints for real-time updates.

This module provides WebSocket endpoints for real-time order status updates
and product/inventory updates using Redis pub/sub for scalable event broadcasting.
"""

import json
import asyncio
import logging
from typing import Dict, Set, Optional, Any
from uuid import UUID

import redis.asyncio as redis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.database import get_db
from app.models.user import User
from app.models.order import Order
from app.auth.jwt import decode_token
from app.auth.permissions import check_resource_ownership, has_minimum_role_level

# Initialize settings and logger
settings = Settings()
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/ws", tags=["websockets"])

# Security scheme for WebSocket authentication
security = HTTPBearer()

# Connection managers for different channels
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        # Dictionary to store active connections by channel
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Redis client for pub/sub
        self.redis_client: Optional[redis.Redis] = None
        # Background tasks
        self._tasks: Set[asyncio.Task] = set()

    async def initialize_redis(self):
        """Initialize Redis connection for pub/sub."""
        try:
            self.redis_client = redis.from_url(settings.redis_url)
            await self.redis_client.ping()
            logger.info("Redis connection established for WebSocket manager")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Continue without Redis for development
            self.redis_client = None

    async def connect(self, websocket: WebSocket, channel: str):
        """Accept WebSocket connection and add to channel."""
        await websocket.accept()

        if channel not in self.active_connections:
            self.active_connections[channel] = set()

        self.active_connections[channel].add(websocket)

        # Start Redis subscription for this channel if not already started
        if self.redis_client and not any(
            task for task in self._tasks
            if not task.done() and task.get_name() == f"redis_sub_{channel}"
        ):
            task = asyncio.create_task(
                self._redis_subscriber(channel),
                name=f"redis_sub_{channel}"
            )
            self._tasks.add(task)

        logger.info(f"WebSocket connected to channel '{channel}'. Active connections: {len(self.active_connections[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove WebSocket connection from channel."""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)

            # Clean up empty channels
            if not self.active_connections[channel]:
                del self.active_connections[channel]

        logger.info(f"WebSocket disconnected from channel '{channel}'. Remaining connections: {len(self.active_connections.get(channel, set()))}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_channel(self, message: str, channel: str):
        """Broadcast message to all connections in a channel."""
        if channel not in self.active_connections:
            return

        # Create a copy of the set to avoid modification during iteration
        connections = self.active_connections[channel].copy()

        for websocket in connections:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                # Remove broken connection
                self.disconnect(websocket, channel)

    async def publish_event(self, channel: str, event_type: str, data: Dict[str, Any]):
        """Publish event to Redis for distribution across instances."""
        if not self.redis_client:
            # Fallback to local broadcast if Redis is not available
            await self.broadcast_to_channel(
                json.dumps({"type": event_type, "data": data}),
                channel
            )
            return

        try:
            message = json.dumps({
                "type": event_type,
                "data": data
            })
            await self.redis_client.publish(channel, message)
            logger.debug(f"Published event '{event_type}' to channel '{channel}'")
        except Exception as e:
            logger.error(f"Error publishing to Redis: {e}")
            # Fallback to local broadcast
            await self.broadcast_to_channel(
                json.dumps({"type": event_type, "data": data}),
                channel
            )

    async def _redis_subscriber(self, channel: str):
        """Background task to subscribe to Redis channel and broadcast messages."""
        if not self.redis_client:
            return

        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(channel)

            logger.info(f"Started Redis subscription for channel '{channel}'")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    await self.broadcast_to_channel(
                        message["data"].decode("utf-8"),
                        channel
                    )
        except Exception as e:
            logger.error(f"Redis subscriber error for channel '{channel}': {e}")
        finally:
            try:
                await pubsub.unsubscribe(channel)
                await pubsub.aclose()
            except:
                pass

# Global connection manager
manager = ConnectionManager()

async def authenticate_websocket(websocket: WebSocket, token: str, db: Session) -> Optional[User]:
    """
    Authenticate WebSocket connection using JWT token.

    Args:
        websocket: WebSocket connection
        token: JWT token for authentication
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    try:
        # Decode token without raising exceptions
        payload = decode_token(token)
        if not payload:
            return None

        user_id_str = payload.get("sub")
        if not user_id_str:
            return None

        user_id = UUID(user_id_str)
        user = db.query(User).filter(User.id == user_id).first()

        if user and user.is_active:
            return user

        return None
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        return None

@router.websocket("/orders/{order_id}")
async def websocket_order_updates(
    websocket: WebSocket,
    order_id: str,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time order status updates.

    Provides real-time updates for order status changes, payment updates,
    and shipping information. Access is restricted to the order owner or
    users with admin privileges.

    **Authentication:**
    - Requires valid JWT token passed as query parameter
    - Only order owner or admin can subscribe to order updates

    **Events:**
    - `order_status_changed`: Order status has been updated
    - `payment_status_changed`: Payment status has been updated
    - `order_shipped`: Order has been shipped with tracking info
    - `order_delivered`: Order has been delivered
    - `order_cancelled`: Order has been cancelled

    **Usage:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/orders/123?token=your_jwt_token');
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('Order update:', data);
    };
    ```
    """
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return

    # Authenticate user
    user = await authenticate_websocket(websocket, token, db)
    if not user:
        await websocket.close(code=4001, reason="Invalid authentication")
        return

    # Validate order ID and check permissions
    try:
        order_uuid = UUID(order_id)
        order = db.query(Order).filter(Order.id == order_uuid).first()

        if not order:
            await websocket.close(code=4004, reason="Order not found")
            return

        # Check if user owns the order or has admin privileges
        if not check_resource_ownership(user, order.user_id):
            await websocket.close(code=4003, reason="Access denied")
            return

    except ValueError:
        await websocket.close(code=4000, reason="Invalid order ID format")
        return

    # Initialize Redis connection if not already done
    if manager.redis_client is None:
        await manager.initialize_redis()

    channel = f"order_{order_id}"

    try:
        await manager.connect(websocket, channel)

        # Send initial order status
        await manager.send_personal_message(
            json.dumps({
                "type": "connection_established",
                "data": {
                    "order_id": order_id,
                    "current_status": order.status.value,
                    "payment_status": order.payment_status.value
                }
            }),
            websocket
        )

        # Keep connection alive
        while True:
            try:
                # Wait for client messages (ping/pong or close)
                data = await websocket.receive_text()

                # Handle ping messages
                if data == "ping":
                    await websocket.send_text("pong")

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in order WebSocket: {e}")
                break

    finally:
        manager.disconnect(websocket, channel)

@router.websocket("/products")
async def websocket_product_updates(
    websocket: WebSocket,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time product and inventory updates.

    Provides real-time updates for product information changes, inventory
    levels, pricing updates, and product availability. Available to all
    authenticated users.

    **Authentication:**
    - Requires valid JWT token passed as query parameter
    - Available to all authenticated users

    **Events:**
    - `product_created`: New product has been added
    - `product_updated`: Product information has been changed
    - `product_deleted`: Product has been removed
