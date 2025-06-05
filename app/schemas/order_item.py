"""
OrderItem Pydantic schemas for request/response serialization.

This module defines schemas for OrderItem model operations including
creation, updates, and responses with proper validation and documentation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from .product import ProductSummary


class OrderItemBase(BaseModel):
    """
    Base OrderItem schema with common fields for creation and updates.

    Contains order item information including product reference, quantity,
    and pricing that can be provided during order item operations.
    """
    product_id: UUID = Field(..., description="ID of the product being ordered")
    quantity: int = Field(..., gt=0, description="Quantity of the product")
    unit_price: Decimal = Field(..., gt=0, description="Price per unit at time of purchase")

    # Product details captured at time of order (for historical record)
    product_name: str = Field(..., min_length=1, max_length=200, description="Product name at time of order")
    product_sku: str = Field(..., min_length=1, max_length=100, description="Product SKU at time of order")
    product_description: Optional[str] = Field(None, max_length=500, description="Product description at time of order")

    @validator('product_name')
    def validate_product_name(cls, v):
        """Validate product name is not empty after stripping."""
        if not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip()

    @validator('product_sku')
    def validate_product_sku(cls, v):
        """Validate product SKU is not empty after stripping."""
        if not v.strip():
            raise ValueError('Product SKU cannot be empty')
        return v.strip().upper()

    @validator('product_description')
    def validate_product_description(cls, v):
        """Clean up product description."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class OrderItemCreate(OrderItemBase):
    """
    Schema for creating a new order item.

    Used when adding items to an order. The order_id is typically set
    by the parent order creation process.
    """
    pass


class OrderItemUpdate(BaseModel):
    """
    Schema for updating an existing order item.

    Allows updating quantity and pricing. Product details are typically
    immutable once an order is placed to maintain historical accuracy.
    """
    quantity: Optional[int] = Field(None, gt=0, description="Quantity of the product")
    unit_price: Optional[Decimal] = Field(None, gt=0, description="Price per unit at time of purchase")


class OrderItemRead(OrderItemBase):
    """
    Schema for reading order item data in API responses.

    Includes all order item information with read-only fields like ID,
    timestamps, and calculated total price. Also includes related product summary.
    """
    id: UUID = Field(..., description="Order item's unique identifier")
    order_id: UUID = Field(..., description="ID of the parent order")
    total_price: Decimal = Field(..., description="Total price (unit_price * quantity)")
    created_at: datetime = Field(..., description="Order item creation timestamp")
    updated_at: datetime = Field(..., description="Last order item update timestamp")
    product: Optional[ProductSummary] = Field(None, description="Associated product summary")

    class Config:
        from_attributes = True


class OrderItemInDB(OrderItemRead):
    """
    Schema representing order item data as stored in database.

    Currently identical to OrderItemRead as order items don't have sensitive fields.
    Kept for consistency and future extensibility.
    """
    pass


class OrderItemSummary(BaseModel):
    """
    Schema for order item summary in nested contexts.

    Contains essential order item information for display in order summaries
    and other contexts where full details aren't needed.
    """
    id: UUID = Field(..., description="Order item's unique identifier")
    product_name: str = Field(..., description="Product name at time of order")
    product_sku: str = Field(..., description="Product SKU at time of order")
    quantity: int = Field(..., description="Quantity of the product")
    unit_price: Decimal = Field(..., description="Price per unit at time of purchase")
    total_price: Decimal = Field(..., description="Total price (unit_price * quantity)")

    class Config:
        from_attributes = True


class OrderItemCreateInternal(BaseModel):
    """
    Internal schema for creating order items with calculated fields.

    Used internally by services to create order items with pre-calculated
    totals and captured product information.
    """
    order_id: UUID = Field(..., description="ID of the parent order")
    product_id: UUID = Field(..., description="ID of the product being ordered")
    quantity: int = Field(..., gt=0, description="Quantity of the product")
    unit_price: Decimal = Field(..., gt=0, description="Price per unit at time of purchase")
    total_price: Decimal = Field(..., gt=0, description="Total price (unit_price * quantity)")
    product_name: str = Field(..., description="Product name at time of order")
    product_sku: str = Field(..., description="Product SKU at time of order")
    product_description: Optional[str] = Field(None, description="Product description at time of order")

    @validator('total_price')
    def validate_total_price(cls, v, values):
        """Validate that total_price matches unit_price * quantity."""
        if 'unit_price' in values and 'quantity' in values:
            expected_total = values['unit_price'] * values['quantity']
            if abs(v - expected_total) > Decimal('0.01'):  # Allow for small rounding differences
                raise ValueError('Total price must equal unit_price * quantity')
        return v
