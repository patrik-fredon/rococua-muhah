from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4
from decimal import Decimal

from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from .order import Order
    from .product import Product


class OrderItem(Base):
    """
    OrderItem model representing individual items within an order.

    This model stores the relationship between orders and products,
    including quantity, pricing at time of purchase, and product
    details captured at the time of order.
    """
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)

    # Foreign keys
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)

    # Quantity and pricing
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)  # Price at time of purchase
    total_price = Column(Numeric(10, 2), nullable=False)  # unit_price * quantity

    # Product details captured at time of order (for historical record)
    product_name = Column(String(200), nullable=False)
    product_sku = Column(String(100), nullable=False)
    product_description = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, product_name='{self.product_name}', quantity={self.quantity}, total_price={self.total_price})>"

    def calculate_total_price(self) -> Decimal:
        """Calculate and return the total price for this order item."""
        return Decimal(str(self.unit_price)) * self.quantity

    def update_total_price(self) -> None:
        """Update the total_price field based on unit_price and quantity."""
        self.total_price = self.calculate_total_price()
