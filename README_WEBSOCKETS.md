# Real-Time WebSocket Infrastructure

This document describes the real-time update infrastructure implemented for the FastAPI project using WebSocket endpoints with Redis pub/sub for scalable event broadcasting.

## Overview

The WebSocket infrastructure provides real-time updates for:

- **Order status changes**: Real-time notifications when orders are updated, shipped, delivered, or cancelled
- **Product and inventory updates**: Live updates for product information, pricing, and stock levels

## Architecture

```
Client (Browser/App)
    ↕ WebSocket Connection
FastAPI Server (WebSocket Endpoints)
    ↕ Redis Pub/Sub
Multiple FastAPI Instances (Scalable Broadcasting)
```

## Features

- ✅ **Authentication**: JWT-based authentication for WebSocket connections
- ✅ **Authorization**: Role-based access control (order owners + admins for orders, all users for products)
- ✅ **Scalability**: Redis pub/sub enables horizontal scaling across multiple server instances
- ✅ **Fallback**: Graceful degradation when Redis is unavailable
- ✅ **Health Monitoring**: Health check endpoint for monitoring connection status
- ✅ **Error Handling**: Robust error handling and connection management

## WebSocket Endpoints

### Order Updates: `/api/v1/ws/orders/{order_id}`

**Purpose**: Real-time updates for specific order status changes.

**Authentication**: Required (JWT token as query parameter)
**Authorization**: Order owner or admin role

**Events**:

- `connection_established`: Sent when WebSocket connection is established
- `order_status_changed`: Order status has been updated
- `payment_status_changed`: Payment status has been updated
- `order_shipped`: Order has been shipped with tracking info
- `order_delivered`: Order has been delivered
- `order_cancelled`: Order has been cancelled

**Usage**:

```javascript
const token = "your_jwt_token";
const orderId = "123e4567-e89b-12d3-a456-426614174000";
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/ws/orders/${orderId}?token=${token}`
);

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Order update:", data);

  switch (data.type) {
    case "order_status_changed":
      updateOrderStatus(data.data.new_status);
      break;
    case "order_shipped":
      showShippingNotification(data.data);
      break;
  }
};
```

### Product Updates: `/api/v1/ws/products`

**Purpose**: Real-time updates for product and inventory changes.

**Authentication**: Required (JWT token as query parameter)
**Authorization**: All authenticated users

**Events**:

- `connection_established`: Sent when WebSocket connection is established
- `product_created`: New product has been added
- `product_updated`: Product information has been changed
- `product_deleted`: Product has been removed
- `inventory_updated`: Product stock quantity has changed
- `price_updated`: Product pricing has been updated
- `product_status_changed`: Product availability status changed

**Usage**:

```javascript
const token = "your_jwt_token";
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/ws/products?token=${token}`
);

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Product update:", data);

  switch (data.type) {
    case "inventory_updated":
      updateProductStock(data.data.product_id, data.data.new_quantity);
      break;
    case "price_updated":
      updateProductPrice(data.data.product_id, data.data.new_price);
      break;
  }
};
```

## Publishing Events

### From Order Service

```python
from app.api.ws import publish_order_update

# When order status changes
await publish_order_update(
    order_id=str(order.id),
    event_type="order_status_changed",
    data={
        "order_id": str(order.id),
        "old_status": "processing",
        "new_status": "shipped",
        "timestamp": datetime.utcnow().isoformat()
    }
)
```

### From Product Service

```python
from app.api.ws import publish_product_update

# When inventory changes
await publish_product_update(
    event_type="inventory_updated",
    data={
        "product_id": str(product.id),
        "sku": product.sku,
        "old_quantity": 10,
        "new_quantity": 5,
        "timestamp": datetime.utcnow().isoformat()
    }
)
```

## Configuration

### Environment Variables

```bash
# Redis Configuration (required for pub/sub)
REDIS_URL=redis://localhost:6379/0

# CORS Settings (required for WebSocket from browsers)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Dependencies

Add to your `requirements.txt`:

```
redis>=5.0.0
websockets>=12.0
```

## Deployment

### Redis Setup

**Development**:

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Using local installation
redis-server
```

**Production**:

- Use Redis Cluster or Redis Sentinel for high availability
- Configure Redis AUTH for security
- Consider Redis persistence settings

### Multiple Server Instances

The Redis pub/sub architecture allows you to run multiple FastAPI instances:

```bash
# Instance 1
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Instance 2
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Instance 3
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

Events published from any instance will be broadcast to WebSocket connections on all instances.

## Monitoring

### Health Check

```bash
curl http://localhost:8000/api/v1/ws/health
```

**Response**:

```json
{
  "status": "healthy",
  "redis_status": "healthy",
  "active_channels": ["order_123", "products"],
  "total_connections": 5,
  "channel_details": {
    "order_123": 2,
    "products": 3
  }
}
```

### Metrics to Monitor

- Number of active WebSocket connections
- Redis connection status
- Message publishing rates
- Connection duration
- Error rates

## Error Handling

### WebSocket Error Codes

- `4000`: Invalid order ID format
- `4001`: Authentication required/failed
- `4003`: Access denied (insufficient permissions)
- `4004`: Order not found

### Client-Side Error Handling

```javascript
ws.onerror = function (error) {
  console.error("WebSocket error:", error);
};

ws.onclose = function (event) {
  if (event.code === 4001) {
    // Redirect to login
    window.location.href = "/login";
  } else {
    // Attempt reconnection
    setTimeout(connectWebSocket, 5000);
  }
};
```

## Security Considerations

1. **Authentication**: All WebSocket connections require valid JWT tokens
2. **Authorization**: Order updates are restricted to order owners and admins
3. **Rate Limiting**: Consider implementing rate limiting for WebSocket connections
4. **Input Validation**: All event data is validated before broadcasting
5. **Redis Security**: Use Redis AUTH and network security in production

## Testing

Run the included test script:

```bash
python test_websockets.py
```

Make sure to:

1. Start your FastAPI server
2. Update the `TEST_TOKEN` with a valid JWT token
3. Ensure Redis is running (optional, fallback mode works without Redis)

## Integration Examples

### React Hook

```javascript
import { useState, useEffect } from "react";

function useOrderUpdates(orderId, token) {
  const [orderStatus, setOrderStatus] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!orderId || !token) return;

    const ws = new WebSocket(
      `ws://localhost:8000/api/v1/ws/orders/${orderId}?token=${token}`
    );

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "order_status_changed") {
        setOrderStatus(data.data.new_status);
      }
    };

    return () => ws.close();
  }, [orderId, token]);

  return { orderStatus, connected };
}
```

### Vue.js Composable

```javascript
import { ref, onMounted, onUnmounted } from "vue";

export function useProductUpdates(token) {
  const products = ref(new Map());
  const connected = ref(false);
  let ws = null;

  onMounted(() => {
    if (!token) return;

    ws = new WebSocket(`ws://localhost:8000/api/v1/ws/products?token=${token}`);

    ws.onopen = () => (connected.value = true);
    ws.onclose = () => (connected.value = false);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "inventory_updated") {
        const product = products.value.get(data.data.product_id);
        if (product) {
          product.stock_quantity = data.data.new_quantity;
        }
      }
    };
  });

  onUnmounted(() => {
    if (ws) ws.close();
  });

  return { products, connected };
}
```
