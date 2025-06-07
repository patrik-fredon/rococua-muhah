"""
Product service layer implementing CRUD operations and business logic.

This module provides product-specific operations extending the base CRUD service
with inventory management, pricing validation, and product-specific business rules.
"""

from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.base import CRUDBase


class ProductService(CRUDBase[Product, ProductCreate, ProductUpdate]):
    """
    Product service with inventory and product management operations.
    """

    def get_by_sku(self, db: Session, *, sku: str) -> Optional[Product]:
        """
        Get product by SKU.

        Args:
            db: Database session
            sku: Product SKU

        Returns:
            Product instance if found, None otherwise
        """
        return db.query(Product).filter(Product.sku == sku).first()

    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Product]:
        """
        Get product by URL slug.

        Args:
            db: Database session
            slug: Product URL slug

        Returns:
            Product instance if found, None otherwise
        """
        return db.query(Product).filter(Product.slug == slug).first()

    def get_active_products(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Get list of active products.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active products
        """
        return self.get_multi(db, skip=skip, limit=limit, filters={"is_active": True})

    def get_featured_products(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Get list of featured products.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of featured products
        """
        return (
            db.query(Product)
            .filter(Product.is_featured == True, Product.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self, db: Session, *, category: str, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Get products by category.

        Args:
            db: Database session
            category: Product category
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of products in category
        """
        return (
            db.query(Product)
            .filter(Product.category == category, Product.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_brand(
        self, db: Session, *, brand: str, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Get products by brand.

        Args:
            db: Database session
            brand: Product brand
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of products by brand
        """
        return (
            db.query(Product)
            .filter(Product.brand == brand, Product.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_in_stock_products(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Get products that are in stock.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of in-stock products
        """
        return (
            db.query(Product)
            .filter(Product.is_active == True, Product.stock_quantity > 0)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_low_stock_products(
        self, db: Session, *, threshold: int = 10
    ) -> List[Product]:
        """
        Get products with low stock levels.

        Args:
            db: Database session
            threshold: Stock level threshold

        Returns:
            List of low-stock products
        """
        return (
            db.query(Product)
            .filter(
                Product.is_active == True,
                Product.track_inventory == True,
                Product.stock_quantity <= threshold,
                Product.stock_quantity > 0,
            )
            .all()
        )

    def get_out_of_stock_products(self, db: Session) -> List[Product]:
        """
        Get products that are out of stock.

        Args:
            db: Database session

        Returns:
            List of out-of-stock products
        """
        return (
            db.query(Product)
            .filter(
                Product.is_active == True,
                Product.track_inventory == True,
                Product.stock_quantity == 0,
            )
            .all()
        )

    def create_product(self, db: Session, *, product_create: ProductCreate) -> Product:
        """
        Create a new product with validation.

        Args:
            db: Database session
            product_create: Product creation data

        Returns:
            Created product instance

        Raises:
            HTTPException: 400 if SKU or slug already exists, or validation fails
        """
        # Check if SKU already exists
        if self.get_by_sku(db, sku=product_create.sku):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product SKU already exists",
            )

        # Check if slug already exists (if provided)
        if product_create.slug and self.get_by_slug(db, slug=product_create.slug):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product slug already exists",
            )

        # Validate pricing
        if product_create.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product price must be greater than 0",
            )

        if product_create.cost_price and product_create.cost_price < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product cost price cannot be negative",
            )

        if (
            product_create.compare_at_price
            and product_create.compare_at_price <= product_create.price
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Compare at price must be greater than selling price",
            )

        return self.create(db, obj_in=product_create)

    def update_stock(
        self, db: Session, *, product: Product, quantity_change: int
    ) -> Product:
        """
        Update product stock quantity.

        Args:
            db: Database session
            product: Product instance
            quantity_change: Positive or negative quantity change

        Returns:
            Updated product instance

        Raises:
            HTTPException: 400 if update would result in negative stock
        """
        if not product.track_inventory:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product does not track inventory",
            )

        new_quantity = product.stock_quantity + quantity_change
        if new_quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock quantity",
            )

        product.stock_quantity = new_quantity
        db.commit()
        db.refresh(product)
        return product

    def set_stock(self, db: Session, *, product: Product, quantity: int) -> Product:
        """
        Set product stock quantity to specific value.

        Args:
            db: Database session
            product: Product instance
            quantity: New stock quantity

        Returns:
            Updated product instance

        Raises:
            HTTPException: 400 if quantity is negative or product doesn't track inventory
        """
        if not product.track_inventory:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product does not track inventory",
            )

        if quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock quantity cannot be negative",
            )

        product.stock_quantity = quantity
        db.commit()
        db.refresh(product)
        return product

    def can_order_quantity(self, product: Product, quantity: int) -> bool:
        """
        Check if a specific quantity can be ordered.

        Args:
            product: Product instance
            quantity: Requested quantity

        Returns:
            True if quantity can be ordered, False otherwise
        """
        if not product.is_active:
            return False

        if not product.track_inventory:
            return True

        if product.stock_quantity >= quantity:
            return True

        return product.allow_backorders

    def delete_product(self, db: Session, *, product: Product) -> Product:
        """
        Delete a product with safety checks.

        Args:
            db: Database session
            product: Product instance to delete

        Returns:
            Deleted product instance

        Raises:
            HTTPException: 400 if product is referenced in orders
        """
        # Check if product is referenced in any order items
        if hasattr(product, "order_items") and product.order_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete product '{product.name}': referenced in {len(product.order_items)} order(s)",
            )

        return self.delete(db, db_obj=product)


# Create service instance
product_service = ProductService(Product)
