"""
Product management API routes.

This module provides RESTful API endpoints for product management,
including CRUD operations with proper authentication and role-based access control.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.models.user import User
from app.auth import require_role, get_current_active_user
from app.services.product_service import product_service

router = APIRouter(prefix="/products", tags=["products"])


# Public endpoints


@router.get("/", response_model=List[ProductRead])
async def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all active products.

    **Public endpoint** - Returns a paginated list of all active products
    with their complete information including pricing and stock status.

    - **skip**: Number of products to skip (for pagination)
    - **limit**: Maximum number of products to return (max 100)

    Only returns active products visible to the public.
    """
    return product_service.get_active_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product_by_id_endpoint(product_id: UUID, db: Session = Depends(get_db)):
    """
    Get product by ID.

    **Public endpoint** - Retrieves complete product information for the
    specified product ID, including pricing, stock status, and metadata.

    - **product_id**: UUID of the product to retrieve

    Only returns active products visible to the public.
    """
    product = product_service.get_or_404(db, product_id)

    # Only allow access to active products for public endpoint
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return product


# Admin-only endpoints


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Create a new product.

    **Admin only endpoint** - Creates a new product with the provided information.
    SKU must be unique and pricing validation is enforced.

    - **name**: Product name (required)
    - **sku**: Unique product SKU (required)
    - **price**: Product selling price (required, must be > 0)
    - **description**: Detailed product description
    - **short_description**: Brief product description
    - **cost_price**: Product cost price
    - **compare_at_price**: Compare at price for discounts
    - **stock_quantity**: Available stock quantity (default: 0)
    - **track_inventory**: Whether to track inventory levels (default: true)
    - **allow_backorders**: Whether to allow backorders (default: false)
    - **weight**: Product weight in kg
    - **dimensions**: Product dimensions
    - **category**: Product category
    - **brand**: Product brand
    - **is_active**: Whether the product is active (default: true)
    - **is_featured**: Whether the product is featured (default: false)
    - **is_digital**: Whether the product is digital (default: false)
    - **slug**: URL-friendly product identifier
    - **meta_title**: SEO meta title
    - **meta_description**: SEO meta description

    Requires admin role for access.
    """
    return product_service.create_product(db, product_create=product_data)


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product_by_id(
    product_id: UUID,
    product_update: ProductUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Update product by ID.

    **Admin only endpoint** - Allows administrators to update product information.
    All fields are optional for partial updates. SKU uniqueness is enforced.

    - **product_id**: UUID of the product to update
    - **name**: Product name
    - **sku**: Unique product SKU
    - **price**: Product selling price (must be > 0)
    - **description**: Detailed product description
    - **short_description**: Brief product description
    - **cost_price**: Product cost price
    - **compare_at_price**: Compare at price for discounts
    - **stock_quantity**: Available stock quantity
    - **track_inventory**: Whether to track inventory levels
    - **allow_backorders**: Whether to allow backorders
    - **weight**: Product weight in kg
    - **dimensions**: Product dimensions
    - **category**: Product category
    - **brand**: Product brand
    - **is_active**: Whether the product is active
    - **is_featured**: Whether the product is featured
    - **is_digital**: Whether the product is digital
    - **slug**: URL-friendly product identifier
    - **meta_title**: SEO meta title
    - **meta_description**: SEO meta description

    Requires admin role for access.
    """
    product = product_service.get_or_404(db, product_id)
    return product_service.update(db, db_obj=product, obj_in=product_update)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_by_id(
    product_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Delete product by ID.

    **Admin only endpoint** - Deletes the specified product. Products that are
    referenced in existing orders cannot be deleted and will return an error.

    - **product_id**: UUID of the product to delete

    Returns 204 No Content on successful deletion.
    Requires admin role for access.
    """
    product = product_service.get_or_404(db, product_id)
    product_service.delete_product(db, product=product)
