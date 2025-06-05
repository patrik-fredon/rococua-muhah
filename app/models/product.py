from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import uuid4
from decimal import Decimal

from sqlalchemy import Column, String, DateTime, Boolean, Text, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from .order_item import OrderItem


class Product(Base):
    """
    Product model representing items available for purchase.

    This model stores product information including pricing, inventory,
    and metadata. Products can be associated with multiple order items
    through orders.
    """
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    sku = Column(String(100), unique=True, index=True, nullable=False)

    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=True)
    compare_at_price = Column(Numeric(10, 2), nullable=True)

    # Inventory
    stock_quantity = Column(Integer, default=0, nullable=False)
    track_inventory = Column(Boolean, default=True, nullable=False)
    allow_backorders = Column(Boolean, default=False, nullable=False)

    # Product attributes
    weight = Column(Numeric(8, 3), nullable=True)  # in kg
    dimensions = Column(String(100), nullable=True)  # e.g., "10x5x2 cm"
    category = Column(String(100), nullable=True, index=True)
    brand = Column(String(100), nullable=True, index=True)

    # Status and visibility
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    is_digital = Column(Boolean, default=False, nullable=False)

    # SEO and metadata
    slug = Column(String(250), unique=True, index=True, nullable=True)
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}', price={self.price})>"

    @property
    def is_in_stock(self) -> bool:
        """Check if product is currently in stock."""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0 or self.allow_backorders
