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
