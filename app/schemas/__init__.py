"""
Pydantic schemas for the application.

This module exports all Pydantic schemas used for request/response
serialization, validation, and documentation in the FastAPI application.
"""

# User schemas
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserRead,
    UserInDB,
    UserPasswordUpdate,
)

# Role schemas
from .role import (
    RoleBase,
    RoleCreate,
    RoleUpdate,
    RoleRead,
    RoleInDB,
)

# Product schemas
from .product import (
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductRead,
    ProductInDB,
    ProductSummary,
)

# Order Item schemas
from .order_item import (
    OrderItemBase,
    OrderItemCreate,
    OrderItemUpdate,
    OrderItemRead,
    OrderItemInDB,
    OrderItemSummary,
    OrderItemCreateInternal,
)

# Order schemas
from .order import (
    OrderStatus,
    PaymentStatus,
    AddressBase,
    OrderBase,
    OrderCreate,
    OrderUpdate,
    OrderRead,
    OrderInDB,
    OrderSummary,
    OrderCreateInternal,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "UserInDB",
    "UserPasswordUpdate",

    # Role schemas
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleRead",
    "RoleInDB",

    # Product schemas
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductRead",
    "ProductInDB",
    "ProductSummary",

    # Order Item schemas
    "OrderItemBase",
    "OrderItemCreate",
    "OrderItemUpdate",
    "OrderItemRead",
    "OrderItemInDB",
    "OrderItemSummary",
    "OrderItemCreateInternal",

    # Order schemas
    "OrderStatus",
    "PaymentStatus",
    "AddressBase",
    "OrderBase",
    "OrderCreate",
    "OrderUpdate",
    "OrderRead",
    "OrderInDB",
    "OrderSummary",
    "OrderCreateInternal",
]
