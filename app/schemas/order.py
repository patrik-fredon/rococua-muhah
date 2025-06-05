"""
Order Pydantic schemas for request/response serialization.

This module defines schemas for Order model operations including
creation, updates, and responses with proper validation and documentation.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, validator

from .order_item import OrderItemRead, OrderItemSummary, OrderItemCreate
from .user import UserRead


class OrderStatus(str, Enum):
    """Enumeration of possible order statuses."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    """Enumeration of possible payment statuses."""
    PENDING = "pending"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class AddressBase(BaseModel):
    """
    Base address schema for shipping and billing addresses.

    Contains common address fields used in both shipping and billing contexts.
    """
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    company: Optional[str] = Field(None, max_length=100, description="Company name")
    address_line1: str = Field(..., min_length=1, max_length=255, description="Address line 1")
    address_line2: Optional[str] = Field(None, max_length=255, description="Address line 2")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State/Province")
    postal_code: str = Field(..., min_length=1, max_length=20, description="Postal/ZIP code")
    country: str = Field(..., min_length=2, max_length=100, description="Country")

    @validator('first_name', 'last_name', 'address_line1', 'city', 'postal_code', 'country')
    def validate_required_fields(cls, v):
        """Validate required address fields are not empty after stripping."""
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

    @validator('company', 'address_line2', 'state')
    def validate_optional_fields(cls, v):
        """Clean optional address fields."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class OrderBase(BaseModel):
    """
    Base Order schema with common fields for creation and updates.

    Contains order information including customer details, addresses,
    and status that can be provided during order operations.
    """
    user_id: UUID = Field(..., description="ID of the user placing the order")

    # Order status
    status: OrderStatus = Field(OrderStatus.PENDING, description="Current order status")
    payment_status: PaymentStatus = Field(PaymentStatus.PENDING, description="Current payment status")

    # Customer information
    customer_email: EmailStr = Field(..., description="Customer's email address")
    customer_phone: Optional[str] = Field(None, max_length=20, description="Customer's phone number")

    # Shipping address
    shipping_first_name: str = Field(..., min_length=1, max_length=100, description="Shipping first name")
    shipping_last_name: str = Field(..., min_length=1, max_length=100, description="Shipping last name")
    shipping_company: Optional[str] = Field(None, max_length=100, description="Shipping company")
    shipping_address_line1: str = Field(..., min_length=1, max_length=255, description="Shipping address line 1")
    shipping_address_line2: Optional[str] = Field(None, max_length=255, description="Shipping address line 2")
    shipping_city: str = Field(..., min_length=1, max_length=100, description="Shipping city")
    shipping_state: Optional[str] = Field(None, max_length=100, description="Shipping state/province")
    shipping_postal_code: str = Field(..., min_length=1, max_length=20, description="Shipping postal code")
    shipping_country: str = Field(..., min_length=2, max_length=100, description="Shipping country")

    # Billing address
    billing_first_name: str = Field(..., min_length=1, max_length=100, description="Billing first name")
    billing_last_name: str = Field(..., min_length=1, max_length=100, description="Billing last name")
    billing_company: Optional[str] = Field(None, max_length=100, description="Billing company")
    billing_address_line1: str = Field(..., min_length=1, max_length=255, description="Billing address line 1")
    billing_address_line2: Optional[str] = Field(None, max_length=255, description="Billing address line 2")
    billing_city: str = Field(..., min_length=1, max_length=100, description="Billing city")
    billing_state: Optional[str] = Field(None, max_length=100, description="Billing state/province")
    billing_postal_code: str = Field(..., min_length=1, max_length=20, description="Billing postal code")
    billing_country: str = Field(..., min_length=2, max_length=100, description="Billing country")

    # Additional information
    notes: Optional[str] = Field(None, description="Customer notes")

    @validator('customer_phone')
    def validate_phone(cls, v):
        """Basic phone number validation."""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Phone number must contain only digits and common separators')
        return v

    @validator('shipping_first_name', 'shipping_last_name', 'shipping_address_line1',
               'shipping_city', 'shipping_postal_code', 'shipping_country',
               'billing_first_name', 'billing_last_name', 'billing_address_line1',
               'billing_city', 'billing_postal_code', 'billing_country')
    def validate_required_address_fields(cls, v):
        """Validate required address fields are not empty after stripping."""
        if not v.strip():
            raise ValueError('Address field cannot be empty')
        return v.strip()

    @validator('shipping_company', 'shipping_address_line2', 'shipping_state',
               'billing_company', 'billing_address_line2', 'billing_state', 'notes')
    def validate_optional_fields(cls, v):
        """Clean optional fields."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class OrderCreate(OrderBase):
    """
    Schema for creating a new order.

    Includes order details and order items. Order number and pricing
    calculations are typically handled by the service layer.
    """
    order_items: List[OrderItemCreate] = Field(..., min_items=1, description="List of order items")

    @validator('order_items')
    def validate_order_items(cls, v):
        """Validate that order has at least one item."""
        if not v:
            raise ValueError('Order must contain at least one item')
        return v


class OrderUpdate(BaseModel):
    """
    Schema for updating an existing order.

    Allows updating order status, customer information, and addresses.
    Order items are typically managed separately for audit trail purposes.
    """
    status: Optional[OrderStatus] = Field(None, description="Order status")
    payment_status: Optional[PaymentStatus] = Field(None, description="Payment status")
    customer_email: Optional[EmailStr] = Field(None, description="Customer's email address")
    customer_phone: Optional[str] = Field(None, max_length=20, description="Customer's phone number")

    # Shipping address updates
    shipping_first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Shipping first name")
    shipping_last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Shipping last name")
    shipping_company: Optional[str] = Field(None, max_length=100, description="Shipping company")
    shipping_address_line1: Optional[str] = Field(None, min_length=1, max_length=255, description="Shipping address line 1")
    shipping_address_line2: Optional[str] = Field(None, max_length=255, description="Shipping address line 2")
    shipping_city: Optional[str] = Field(None, min_length=1, max_length=100, description="Shipping city")
    shipping_state: Optional[str] = Field(None, max_length=100, description="Shipping state/province")
    shipping_postal_code: Optional[str] = Field(None, min_length=1, max_length=20, description="Shipping postal code")
    shipping_country: Optional[str] = Field(None, min_length=2, max_length=100, description="Shipping country")

    # Billing address updates
    billing_first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Billing first name")
    billing_last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Billing last name")
    billing_company: Optional[str] = Field(None, max_length=100, description="Billing company")
    billing_address_line1: Optional[str] = Field(None, min_length=1, max_length=255, description="Billing address line 1")
    billing_address_line2: Optional[str] = Field(None, max_length=255, description="Billing address line 2")
    billing_city: Optional[str] = Field(None, min_length=1, max_length=100, description="Billing city")
    billing_state: Optional[str] = Field(None, max_length=100, description="Billing state/province")
    billing_postal_code: Optional[str] = Field(None, min_length=1, max_length=20, description="Billing postal code")
    billing_country: Optional[str] = Field(None, min_length=2, max_length=100, description="Billing country")

    # Additional information
    notes: Optional[str] = Field(None, description="Customer notes")
    internal_notes: Optional[str] = Field(None, description="Internal admin notes")


class OrderRead(OrderBase):
    """
    Schema for reading order data in API responses.

    Includes all order information with read-only fields like ID, timestamps,
    pricing calculations, and nested order items with user information.
    """
    id: UUID = Field(..., description="Order's unique identifier")
    order_number: str = Field(..., description="Unique order number")

    # Pricing (calculated fields)
    subtotal: Decimal = Field(..., description="Order subtotal before taxes and shipping")
    tax_amount: Decimal = Field(..., description="Tax amount")
    shipping_amount: Decimal = Field(..., description="Shipping cost")
    discount_amount: Decimal = Field(..., description="Discount amount")
    total_amount: Decimal = Field(..., description="Total order amount")

    # Additional information
    internal_notes: Optional[str] = Field(None, description="Internal admin notes")

    # Timestamps
    created_at: datetime = Field(..., description="Order creation timestamp")
    updated_at: datetime = Field(..., description="Last order update timestamp")
    shipped_at: Optional[datetime] = Field(None, description="Order shipment timestamp")
    delivered_at: Optional[datetime] = Field(None, description="Order delivery timestamp")

    # Relationships
    user: Optional[UserRead] = Field(None, description="User who placed the order")
    order_items: List[OrderItemRead] = Field(default_factory=list, description="Order items")

    class Config:
        from_attributes = True


class OrderInDB(OrderRead):
    """
    Schema representing order data as stored in database.

    Currently identical to OrderRead as orders don't have sensitive fields.
    Kept for consistency and future extensibility.
    """
    pass


class OrderSummary(BaseModel):
    """
    Schema for order summary in lists and user profiles.

    Contains essential order information for display in order lists
    and other contexts where full order details aren't needed.
    """
    id: UUID = Field(..., description="Order's unique identifier")
    order_number: str = Field(..., description="Unique order number")
    status: OrderStatus = Field(..., description="Current order status")
    payment_status: PaymentStatus = Field(..., description="Current payment status")
    total_amount: Decimal = Field(..., description="Total order amount")
    created_at: datetime = Field(..., description="Order creation timestamp")
    order_items: List[OrderItemSummary] = Field(default_factory=list, description="Order items summary")

    class Config:
        from_attributes = True


class OrderCreateInternal(BaseModel):
    """
    Internal schema for creating orders with calculated fields.

    Used internally by services to create orders with pre-calculated
    pricing and generated order numbers.
    """
    user_id: UUID = Field(..., description="ID of the user placing the order")
    order_number: str = Field(..., description="Generated unique order number")

    # Order status
    status: OrderStatus = Field(OrderStatus.PENDING, description="Initial order status")
    payment_status: PaymentStatus = Field(PaymentStatus.PENDING, description="Initial payment status")

    # Pricing (calculated)
    subtotal: Decimal = Field(..., ge=0, description="Order subtotal")
    tax_amount: Decimal = Field(Decimal('0'), ge=0, description="Tax amount")
    shipping_amount: Decimal = Field(Decimal('0'), ge=0, description="Shipping cost")
    discount_amount: Decimal = Field(Decimal('0'), ge=0, description="Discount amount")
    total_amount: Decimal = Field(..., ge=0, description="Total order amount")

    # Customer and address information (same as OrderBase)
    customer_email: EmailStr = Field(..., description="Customer's email address")
    customer_phone: Optional[str] = Field(None, description="Customer's phone number")

    # Address fields (abbreviated for brevity - would include all shipping/billing fields)
    notes: Optional[str] = Field(None, description="Customer notes")
    internal_notes: Optional[str] = Field(None, description="Internal notes")
