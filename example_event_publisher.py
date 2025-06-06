#!/usr/bin/env python3
"""
Example service demonstrating how to publish events to WebSocket subscribers.

This shows how other parts of your application (order processing, inventory management)
can publish real-time updates to connected WebSocket clients.
"""

import asyncio
from datetime import datetime
from uuid import uuid4

# Import the event publishing functions
from app.api.ws import publish_order_update, publish_product_update


async def simulate_order_processing():
    """
    Simulate order processing with real-time updates.

    This demonstrates how an order processing service would publish
    events as the order moves through different stages.
    """
    order_id = str(uuid4())
    print(f"🚀 Starting order processing simulation for order {order_id}")

    # Order confirmed
    await publish_order_update(
        order_id=order_id,
        event_type="order_status_changed",
        data={
            "order_id": order_id,
            "old_status": "pending",
            "new_status": "confirmed",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Order has been confirmed and is being processed"
        }
    )
    print("📦 Order confirmed")
    await asyncio.sleep(2)

    # Payment processed
    await publish_order_update(
        order_id=order_id,
        event_type="payment_status_changed",
        data={
            "order_id": order_id,
            "old_status": "pending",
            "new_status": "paid",
            "amount": 99.99,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Payment has been successfully processed"
        }
    )
    print("💳 Payment processed")
    await asyncio.sleep(3)

    # Order processing
    await publish_order_update(
        order_id=order_id,
        event_type="order_status_changed",
        data={
            "order_id": order_id,
            "old_status": "confirmed",
            "new_status": "processing",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Order is being prepared for shipment"
        }
    )
    print("⚙️ Order processing")
    await asyncio.sleep(4)

    # Order shipped
    tracking_number = f"TRK{uuid4().hex[:8].upper()}"
    await publish_order_update(
        order_id=order_id,
        event_type="order_shipped",
        data={
            "order_id": order_id,
            "old_status": "processing",
            "new_status": "shipped",
            "tracking_number": tracking_number,
            "carrier": "FastShip Express",
            "estimated_delivery": "2024-12-10",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Order has been shipped with tracking number {tracking_number}"
        }
    )
    print(f"🚚 Order shipped with tracking: {tracking_number}")
    await asyncio.sleep(2)

    # Order delivered
    await publish_order_update(
        order_id=order_id,
        event_type="order_delivered",
        data={
            "order_id": order_id,
            "old_status": "shipped",
            "new_status": "delivered",
            "delivered_at": datetime.utcnow().isoformat(),
            "signature": "Customer Signature",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Order has been successfully delivered"
        }
    )
    print("✅ Order delivered")


async def simulate_inventory_updates():
    """
    Simulate inventory management with real-time updates.

    This demonstrates how an inventory management service would publish
    events when stock levels change.
    """
    product_id = str(uuid4())
    print(f"📦 Starting inventory simulation for product {product_id}")

    # Initial stock update
    await publish_product_update(
        event_type="inventory_updated",
        data={
            "product_id": product_id,
            "sku": "PROD-001",
            "name": "Wireless Headphones",
            "old_quantity": 0,
            "new_quantity": 100,
            "warehouse": "Main Warehouse",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "New stock received"
        }
    )
    print("📈 Stock added: 100 units")
    await asyncio.sleep(2)

    # Purchase reduces stock
    await publish_product_update(
        event_type="inventory_updated",
        data={
            "product_id": product_id,
            "sku": "PROD-001",
            "name": "Wireless Headphones",
            "old_quantity": 100,
            "new_quantity": 95,
            "change_reason": "customer_purchase",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Stock reduced due to customer purchase"
        }
    )
    print("📉 Stock reduced: 95 units remaining")
    await asyncio.sleep(1)

    # Price update
    await publish_product_update(
        event_type="price_updated",
        data={
            "product_id": product_id,
            "sku": "PROD-001",
            "name": "Wireless Headphones",
            "old_price": 99.99,
            "new_price": 89.99,
            "discount_percentage": 10,
            "sale_end_date": "2024-12-15",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Holiday sale price activated"
        }
    )
    print("💰 Price updated: $89.99 (10% off)")
    await asyncio.sleep(2)

    # Low stock warning
    await publish_product_update(
        event_type="inventory_updated",
        data={
            "product_id": product_id,
            "sku": "PROD-001",
            "name": "Wireless Headphones",
            "old_quantity": 95,
            "new_quantity": 5,
            "low_stock_threshold": 10,
            "alert_level": "warning",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Low stock alert: Only 5 units remaining"
        }
    )
    print("⚠️ Low stock warning: 5 units remaining")


async def simulate_product_lifecycle():
    """
    Simulate a complete product lifecycle with real-time updates.
    """
    product_id = str(uuid4())
    print(f"🆕 Starting product lifecycle simulation for {product_id}")

    # Product created
    await publish_product_update(
        event_type="product_created",
        data={
            "product_id": product_id,
            "sku": "PROD-002",
            "name": "Smart Watch",
            "category": "Electronics",
            "price": 299.99,
            "initial_stock": 50,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "New product added to catalog"
        }
    )
    print("🆕 Product created: Smart Watch")
    await asyncio.sleep(2)

    # Product updated
    await publish_product_update(
        event_type="product_updated",
        data={
            "product_id": product_id,
            "sku": "PROD-002",
            "name": "Smart Watch Pro",  # Name updated
            "fields_updated": ["name", "description", "features"],
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Product information updated"
        }
    )
    print("📝 Product updated: Smart Watch Pro")
    await asyncio.sleep(2)

    # Product status changed
    await publish_product_update(
        event_type="product_status_changed",
        data={
            "product_id": product_id,
            "sku": "PROD-002",
            "name": "Smart Watch Pro",
            "old_status": "active",
            "new_status": "discontinued",
            "reason": "end_of_life",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Product discontinued - end of product lifecycle"
        }
    )
    print("🚫 Product discontinued")


async def main():
    """
    Main function to run all simulations.

    This demonstrates how different services in your application
    can publish real-time events to WebSocket subscribers.
    """
    print("🌟 WebSocket Event Publishing Simulation")
    print("=" * 50)
    print("This simulation shows how to publish real-time events")
    print("that will be broadcast to connected WebSocket clients.")
    print()
    print("⚠️  Note: This will work even without Redis (fallback mode)")
    print("   For full scalability, ensure Redis is running.")
    print()

    # Run simulations concurrently
    tasks = [
        simulate_order_processing(),
        simulate_inventory_updates(),
        simulate_product_lifecycle()
    ]

    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print("✅ All simulations completed!")
    print("💡 In a real application, these events would be published")
    print("   from your business logic when actual changes occur.")


if __name__ == "__main__":
    print("WebSocket Event Publishing Example")
    print("==================================")
    asyncio.run(main())
