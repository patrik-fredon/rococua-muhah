#!/usr/bin/env python3
"""
Test script for WebSocket endpoints.

This script demonstrates how to connect to and test the WebSocket endpoints
for real-time order and product updates.
"""

import asyncio
import json
import websockets
from urllib.parse import urlencode

# Test configuration
BASE_URL = "ws://localhost:8000"
API_PREFIX = "/api/v1"

# Example JWT token (replace with a real token from your authentication)
TEST_TOKEN = "your_jwt_token_here"

async def test_order_websocket(order_id: str, token: str):
    """Test order updates WebSocket endpoint."""
    uri = f"{BASE_URL}{API_PREFIX}/ws/orders/{order_id}?token={token}"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to order WebSocket for order {order_id}")

            # Listen for messages
            async for message in websocket:
                data = json.loads(message)
                print(f"📨 Order update: {data}")

                # Send ping to keep connection alive
                if data.get("type") == "connection_established":
                    await websocket.send("ping")

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ Order WebSocket connection closed: {e}")
    except Exception as e:
        print(f"❌ Error in order WebSocket: {e}")

async def test_products_websocket(token: str):
    """Test product updates WebSocket endpoint."""
    uri = f"{BASE_URL}{API_PREFIX}/ws/products?token={token}"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to products WebSocket")

            # Listen for messages
            async for message in websocket:
                data = json.loads(message)
                print(f"📨 Product update: {data}")

                # Send ping to keep connection alive
                if data.get("type") == "connection_established":
                    await websocket.send("ping")

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ Products WebSocket connection closed: {e}")
    except Exception as e:
        print(f"❌ Error in products WebSocket: {e}")

async def test_websocket_health():
    """Test WebSocket health endpoint."""
    import aiohttp

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://localhost:8000{API_PREFIX}/ws/health") as response:
                data = await response.json()
                print(f"🏥 WebSocket Health: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"❌ Error checking WebSocket health: {e}")

async def main():
    """Main test function."""
    print("🚀 Testing WebSocket endpoints...")
    print("⚠️  Make sure your FastAPI server is running on localhost:8000")
    print("⚠️  Replace TEST_TOKEN with a valid JWT token")
    print()

    # Test health endpoint first
    await test_websocket_health()
    print()

    if TEST_TOKEN == "your_jwt_token_here":
        print("❌ Please update TEST_TOKEN with a valid JWT token")
        print("💡 You can get a token by calling the /api/v1/auth/login endpoint")
        return

    # Test order WebSocket (replace with a real order ID)
    test_order_id = "123e4567-e89b-12d3-a456-426614174000"

    # Run tests concurrently
    await asyncio.gather(
        test_order_websocket(test_order_id, TEST_TOKEN),
        test_products_websocket(TEST_TOKEN),
        return_exceptions=True
    )

if __name__ == "__main__":
    print("WebSocket Test Script")
    print("===================")
    asyncio.run(main())
