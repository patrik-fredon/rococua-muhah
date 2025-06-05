"""
Product Pydantic schemas for request/response serialization.

This module defines schemas for Product model operations including
creation, updates, and responses with proper validation and documentation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class ProductBase(BaseModel):
    """
    Base Product schema with common fields for creation and updates.

    Contains product information including pricing, inventory, and metadata
    that can be provided during product creation or modification operations.
    """
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Detailed product description")
    short_description: Optional[str] = Field(None, max_length=500, description="Brief product description")
    sku: str = Field(..., min_length=1, max_length=100, description="Unique product SKU")

    # Pricing
    price: Decimal = Field(..., gt=0, description="Product selling price")
    cost_price: Optional[Decimal] = Field(None, ge=0, description="Product cost price")
    compare_at_price: Optional[Decimal] = Field(None, ge=0, description="Compare at price for discounts")

    # Inventory
    stock_quantity: int = Field(0, ge=0, description="Available stock quantity")
    track_inventory: bool = Field(True, description="Whether to track inventory levels")
    allow_backorders: bool = Field(False, description="Whether to allow backorders when out of stock")

    # Product attributes
    weight: Optional[Decimal] = Field(None, ge=0, description="Product weight in kg")
    dimensions: Optional[str] = Field(None, max_length=100, description="Product dimensions (e.g., '10x5x2 cm')")
    category: Optional[str] = Field(None, max_length=100, description="Product category")
    brand: Optional[str] = Field(None, max_length=100, description="Product brand")

    # Status and visibility
    is_active: bool = Field(True, description="Whether the product is active and visible")
    is_featured: bool = Field(False, description="Whether the product is featured")
    is_digital: bool = Field(False, description="Whether the product is digital (no shipping required)")

    # SEO and metadata
    slug: Optional[str] = Field(None, max_length=250, description="URL-friendly product identifier")
    meta_title: Optional[str] = Field(None, max_length=200, description="SEO meta title")
    meta_description: Optional[str] = Field(None, max_length=500, description="SEO meta description")

    @validator('name')
    def validate_name(cls, v):
        """Validate product name is not empty after stripping."""
        if not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip()

    @validator('sku')
    def validate_sku(cls, v):
        """Validate SKU format."""
        if not v.strip():
            raise ValueError('SKU cannot be empty')
        # Remove spaces and convert to uppercase for consistency
        return v.strip().upper().replace(' ', '')

    @validator('compare_at_price')
    def validate_compare_at_price(cls, v, values):
        """Validate compare_at_price is greater than price when provided."""
        if v is not None and 'price' in values and values['price'] is not None:
            if v <= values['price']:
                raise ValueError('Compare at price must be greater than selling price')
        return v

    @validator('cost_price')
    def validate_cost_price(cls, v, values):
        """Validate cost_price is less than or equal to price when provided."""
        if v is not None and 'price' in values and values['price'] is not None:
            if v > values['price']:
                raise ValueError('Cost price should not exceed selling price')
        return v

    @validator('slug')
    def validate_slug(cls, v):
        """Validate slug format."""
        if v is not None:
            v = v.strip().lower()
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Slug must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @validator('dimensions')
    def validate_dimensions(cls, v):
        """Basic validation for dimensions format."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class ProductCreate(ProductBase):
    """
    Schema for creating a new product.

    Inherits all fields from ProductBase. Required fields are name, sku, and price.
    """
    pass


class ProductUpdate(BaseModel):
    """
    Schema for updating an existing product.

    All fields are optional to allow partial updates. SKU uniqueness
    will be validated at the database level.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Detailed product description")
    short_description: Optional[str] = Field(None, max_length=500, description="Brief product description")
    sku: Optional[str] = Field(None, min_length=1, max_length=100, description="Unique product SKU")

    # Pricing
    price: Optional[Decimal] = Field(None, gt=0, description="Product selling price")
    cost_price: Optional[Decimal] = Field(None, ge=0, description="Product cost price")
    compare_at_price: Optional[Decimal] = Field(None, ge=0, description="Compare at price for discounts")

    # Inventory
    stock_quantity: Optional[int] = Field(None, ge=0, description="Available stock quantity")
    track_inventory: Optional[bool] = Field(None, description="Whether to track inventory levels")
    allow_backorders: Optional[bool] = Field(None, description="Whether to allow backorders when out of stock")

    # Product attributes
    weight: Optional[Decimal] = Field(None, ge=0, description="Product weight in kg")
    dimensions: Optional[str] = Field(None, max_length=100, description="Product dimensions")
    category: Optional[str] = Field(None, max_length=100, description="Product category")
    brand: Optional[str] = Field(None, max_length=100, description="Product brand")

    # Status and visibility
    is_active: Optional[bool] = Field(None, description="Whether the product is active and visible")
    is_featured: Optional[bool] = Field(None, description="Whether the product is featured")
    is_digital: Optional[bool] = Field(None, description="Whether the product is digital")

    # SEO and metadata
    slug: Optional[str] = Field(None, max_length=250, description="URL-friendly product identifier")
    meta_title: Optional[str] = Field(None, max_length=200, description="SEO meta title")
    meta_description: Optional[str] = Field(None, max_length=500, description="SEO meta description")

    @validator('name')
    def validate_name(cls, v):
        """Validate product name is not empty after stripping."""
        if v is not None:
            if not v.strip():
                raise ValueError('Product name cannot be empty')
            return v.strip()
        return v

    @validator('sku')
    def validate_sku(cls, v):
        """Validate SKU format."""
        if v is not None:
            if not v.strip():
                raise ValueError('SKU cannot be empty')
            return v.strip().upper().replace(' ', '')
        return v

    @validator('slug')
    def validate_slug(cls, v):
        """Validate slug format."""
        if v is not None:
            v = v.strip().lower()
            if v and not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Slug must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @validator('dimensions')
    def validate_dimensions(cls, v):
        """Basic validation for dimensions format."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class ProductRead(ProductBase):
    """
    Schema for reading product data in API responses.

    Includes all product information with read-only fields like ID and timestamps.
    Also includes computed properties like stock status.
    """
    id: UUID = Field(..., description="Product's unique identifier")
    created_at: datetime = Field(..., description="Product creation timestamp")
    updated_at: datetime = Field(..., description="Last product update timestamp")
    is_in_stock: bool = Field(..., description="Whether the product is currently in stock")

    class Config:
        from_attributes = True


class ProductInDB(ProductRead):
    """
    Schema representing product data as stored in database.

    Currently identical to ProductRead as products don't have sensitive fields.
    Kept for consistency and future extensibility.
    """
    pass


class ProductSummary(BaseModel):
    """
    Schema for product summary in lists and nested objects.

    Contains essential product information for display in order items
    and other contexts where full product details aren't needed.
    """
    id: UUID = Field(..., description="Product's unique identifier")
    name: str = Field(..., description="Product name")
    sku: str = Field(..., description="Product SKU")
    price: Decimal = Field(..., description="Product selling price")
    is_active: bool = Field(..., description="Whether the product is active")
    is_in_stock: bool = Field(..., description="Whether the product is currently in stock")

    class Config:
        from_attributes = True
