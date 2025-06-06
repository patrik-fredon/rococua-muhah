"""
Product management API routes.

This module provides RESTful API endpoints for product management,
including CRUD operations with proper authentication and role-based access control.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.models.product import Product
from app.models.user import User
from app.auth import require_role, get_current_active_user

router = APIRouter(prefix="/api/v1/products", tags=["products"])


def get_product_by_id(db: Session, product_id: UUID) -> Product:
    """
    Get a product by ID.

    Args:
        db: Database session
        product_id: Product's unique identifier

    Returns:
        Product object if found

    Raises:
        HTTPException: If product not found
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


def create_product_service(db: Session, product_create: ProductCreate) -> Product:
    """
    Create a new product.

    Args:
        db: Database session
        product_create: Product creation data

    Returns:
        Created product object

    Raises:
        HTTPException: If product creation fails
    """
    try:
        product = Product(
            name=product_create.name,
            description=product_create.description,
            short_description=product_create.short_description,
            sku=product_create.sku,
            price=product_create.price,
            cost_price=product_create.cost_price,
            compare_at_price=product_create.compare_at_price,
            stock_quantity=product_create.stock_quantity,
            track_inventory=product_create.track_inventory,
            allow_backorders=product_create.allow_backorders,
            weight=product_create.weight,
            dimensions=product_create.dimensions,
            category=product_create.category,
            brand=product_create.brand,
            is_active=product_create.is_active,
            is_featured=product_create.is_featured,
            is_digital=product_create.is_digital,
            slug=product_create.slug,
            meta_title=product_create.meta_title,
            meta_description=product_create.meta_description
        )

        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    except IntegrityError as e:
        db.rollback()
        if "sku" in str(e.orig).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product SKU already exists"
            )
        elif "slug" in str(e.orig).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product slug already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create product: constraint violation"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product: internal server error"
        )


def update_product_service(db: Session, product: Product, product_update: ProductUpdate) -> Product:
    """
    Update an existing product.

    Args:
        db: Database session
        product: Product object to update
        product_update: Product update data

    Returns:
        Updated product object

    Raises:
        HTTPException: If product update fails
    """
    try:
        # Update product fields
        update_data = product_update.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(product, field, value)

        db.commit()
        db.refresh(product)
        return product

    except IntegrityError as e:
        db.rollback()
        if "sku" in str(e.orig).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product SKU already exists"
            )
        elif "slug" in str(e.orig).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product slug already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update product: constraint violation"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product: internal server error"
        )


def delete_product_service(db: Session, product: Product) -> None:
    """
    Delete a product.

    Args:
        db: Database session
        product: Product object to delete

    Raises:
        HTTPException: If product deletion fails
    """
    try:
        # Check if product is referenced in any order items
        if product.order_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete product '{product.name}': referenced in {len(product.order_items)} order(s)"
            )

        db.delete(product)
        db.commit()

    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product: internal server error"
        )


# Public endpoints

@router.get("/", response_model=List[ProductRead])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all active products.

    **Public endpoint** - Returns a paginated list of all active products
    with their complete information including pricing and stock status.

    - **skip**: Number of products to skip (for pagination)
    - **limit**: Maximum number of products to return (max 100)

    Only returns active products visible to the public.
    """
    products = db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductRead)
async def get_product_by_id_endpoint(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get product by ID.

    **Public endpoint** - Retrieves complete product information for the
    specified product ID, including pricing, stock status, and metadata.

    - **product_id**: UUID of the product to retrieve

    Only returns active products visible to the public.
    """
    product = get_product_by_id(db, product_id)

    # Only allow access to active products for public endpoint
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


# Admin-only endpoints

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
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
    return create_product_service(db, product_data)


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product_by_id(
    product_id: UUID,
    product_update: ProductUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
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
    product = get_product_by_id(db, product_id)
    return update_product_service(db, product, product_update)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_by_id(
    product_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Delete product by ID.

    **Admin only endpoint** - Deletes the specified product. Products that are
    referenced in existing orders cannot be deleted and will return an error.

    - **product_id**: UUID of the product to delete

    Returns 204 No Content on successful deletion.
    Requires admin role for access.
    """
    product = get_product_by_id(db, product_id)
    delete_product_service(db, product)
