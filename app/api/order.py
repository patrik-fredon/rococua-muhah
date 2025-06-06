"""
Order management API routes.

This module provides RESTful API endpoints for order and order item management,
including CRUD operations with proper authentication and role-based access control.
"""

from typing import List
from uuid import UUID
from decimal import Decimal
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.schemas.order import OrderCreate, OrderRead, OrderUpdate, OrderSummary
from app.schemas.order_item import OrderItemCreate, OrderItemRead, OrderItemUpdate
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User
from app.auth import (
    require_role,
    get_current_active_user,
    check_resource_ownership
)

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


def generate_order_number() -> str:
    """
    Generate a unique order number.

    Returns:
        Unique order number string
    """
    # Generate a random order number with prefix
    random_part = ''.join(secrets.choice(string.digits) for _ in range(8))
    return f"ORD-{random_part}"


def get_order_by_id(db: Session, order_id: UUID) -> Order:
    """
    Get an order by ID.

    Args:
        db: Database session
        order_id: Order's unique identifier

    Returns:
        Order object if found

    Raises:
        HTTPException: If order not found
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


def get_order_item_by_id(db: Session, order_item_id: UUID) -> OrderItem:
    """
    Get an order item by ID.

    Args:
        db: Database session
        order_item_id: Order item's unique identifier

    Returns:
        OrderItem object if found

    Raises:
        HTTPException: If order item not found
    """
    order_item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    return order_item


def calculate_order_totals(order_items: List[OrderItemCreate], db: Session) -> dict:
    """
    Calculate order totals based on order items.

    Args:
        order_items: List of order items to calculate totals for
        db: Database session

    Returns:
        Dictionary with calculated totals
    """
    subtotal = Decimal('0')

    for item in order_items:
        # Verify product exists and get current price
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with ID {item.product_id} not found"
            )

        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is not available"
            )

        # Use product's current price if not specified in order item
        unit_price = item.unit_price if hasattr(item, 'unit_price') and item.unit_price else product.price
        item_total = unit_price * item.quantity
        subtotal += item_total

    # Simple tax calculation (you can make this more sophisticated)
    tax_rate = Decimal('0.10')  # 10% tax
    tax_amount = subtotal * tax_rate

    # For simplicity, no shipping and discount for now
    shipping_amount = Decimal('0')
    discount_amount = Decimal('0')

    total_amount = subtotal + tax_amount + shipping_amount - discount_amount

    return {
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'shipping_amount': shipping_amount,
        'discount_amount': discount_amount,
        'total_amount': total_amount
    }


def create_order_service(db: Session, order_create: OrderCreate, current_user: User) -> Order:
    """
    Create a new order with order items.

    Args:
        db: Database session
        order_create: Order creation data
        current_user: User creating the order

    Returns:
        Created order object

    Raises:
        HTTPException: If order creation fails
    """
    try:
        # Calculate order totals
        totals = calculate_order_totals(order_create.order_items, db)

        # Generate unique order number
        order_number = generate_order_number()

        # Ensure order number is unique
        while db.query(Order).filter(Order.order_number == order_number).first():
            order_number = generate_order_number()

        # Create order
        order = Order(
            order_number=order_number,
            user_id=current_user.id,
            status=order_create.status,
            payment_status=order_create.payment_status,
            subtotal=totals['subtotal'],
            tax_amount=totals['tax_amount'],
            shipping_amount=totals['shipping_amount'],
            discount_amount=totals['discount_amount'],
            total_amount=totals['total_amount'],
            customer_email=order_create.customer_email,
            customer_phone=order_create.customer_phone,
            shipping_first_name=order_create.shipping_first_name,
            shipping_last_name=order_create.shipping_last_name,
            shipping_company=order_create.shipping_company,
            shipping_address_line1=order_create.shipping_address_line1,
            shipping_address_line2=order_create.shipping_address_line2,
            shipping_city=order_create.shipping_city,
            shipping_state=order_create.shipping_state,
            shipping_postal_code=order_create.shipping_postal_code,
            shipping_country=order_create.shipping_country,
            billing_first_name=order_create.billing_first_name,
            billing_last_name=order_create.billing_last_name,
            billing_company=order_create.billing_company,
            billing_address_line1=order_create.billing_address_line1,
            billing_address_line2=order_create.billing_address_line2,
            billing_city=order_create.billing_city,
            billing_state=order_create.billing_state,
            billing_postal_code=order_create.billing_postal_code,
            billing_country=order_create.billing_country,
            notes=order_create.notes
        )

        db.add(order)
        db.flush()  # Get the order ID before creating order items

        # Create order items
        for item_create in order_create.order_items:
            # Get product details
            product = db.query(Product).filter(Product.id == item_create.product_id).first()
            unit_price = item_create.unit_price if hasattr(item_create, 'unit_price') and item_create.unit_price else product.price

            order_item = OrderItem(
                order_id=order.id,
                product_id=item_create.product_id,
                quantity=item_create.quantity,
                unit_price=unit_price,
                total_price=unit_price * item_create.quantity,
                product_name=item_create.product_name,
                product_sku=item_create.product_sku,
                product_description=item_create.product_description
            )
            db.add(order_item)

        db.commit()
        db.refresh(order)
        return order

    except HTTPException:
        # Re-raise HTTPExceptions as-is
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order: internal server error"
        )


def update_order_service(db: Session, order: Order, order_update: OrderUpdate) -> Order:
    """
    Update an existing order.

    Args:
        db: Database session
        order: Order object to update
        order_update: Order update data

    Returns:
        Updated order object

    Raises:
        HTTPException: If order update fails
    """
    try:
        # Update order fields
        update_data = order_update.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(order, field, value)

        db.commit()
        db.refresh(order)
        return order

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order: internal server error"
        )


def create_order_item_service(db: Session, order: Order, item_create: OrderItemCreate) -> OrderItem:
    """
    Add a new item to an existing order.

    Args:
        db: Database session
        order: Order to add item to
        item_create: Order item creation data

    Returns:
        Created order item object

    Raises:
        HTTPException: If order item creation fails
    """
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == item_create.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with ID {item_create.product_id} not found"
            )

        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is not available"
            )

        # Use product's current price if not specified
        unit_price = item_create.unit_price if hasattr(item_create, 'unit_price') and item_create.unit_price else product.price

        order_item = OrderItem(
            order_id=order.id,
            product_id=item_create.product_id,
            quantity=item_create.quantity,
            unit_price=unit_price,
            total_price=unit_price * item_create.quantity,
            product_name=item_create.product_name,
            product_sku=item_create.product_sku,
            product_description=item_create.product_description
        )

        db.add(order_item)
        db.commit()
        db.refresh(order_item)

        # Recalculate order totals
        # This is a simplified version - in production you might want to be more sophisticated
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        new_subtotal = sum(item.total_price for item in order_items)
        new_tax_amount = new_subtotal * Decimal('0.10')
        new_total_amount = new_subtotal + new_tax_amount + order.shipping_amount - order.discount_amount

        order.subtotal = new_subtotal
        order.tax_amount = new_tax_amount
        order.total_amount = new_total_amount
        db.commit()

        return order_item

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add order item: internal server error"
        )


def update_order_item_service(db: Session, order_item: OrderItem, item_update: OrderItemUpdate) -> OrderItem:
    """
    Update an existing order item.

    Args:
        db: Database session
        order_item: Order item to update
        item_update: Order item update data

    Returns:
        Updated order item object

    Raises:
        HTTPException: If order item update fails
    """
    try:
        # Update order item fields
        update_data = item_update.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(order_item, field, value)

        # Recalculate total price if quantity or unit_price changed
        if 'quantity' in update_data or 'unit_price' in update_data:
            order_item.total_price = order_item.unit_price * order_item.quantity

        db.commit()
        db.refresh(order_item)

        # Recalculate order totals
        order = db.query(Order).filter(Order.id == order_item.order_id).first()
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        new_subtotal = sum(item.total_price for item in order_items)
        new_tax_amount = new_subtotal * Decimal('0.10')
        new_total_amount = new_subtotal + new_tax_amount + order.shipping_amount - order.discount_amount

        order.subtotal = new_subtotal
        order.tax_amount = new_tax_amount
        order.total_amount = new_total_amount
        db.commit()

        return order_item

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order item: internal server error"
        )


def delete_order_item_service(db: Session, order_item: OrderItem) -> None:
    """
    Remove an order item from an order.

    Args:
        db: Database session
        order_item: Order item to remove

    Raises:
        HTTPException: If order item deletion fails
    """
    try:
        order_id = order_item.order_id
        db.delete(order_item)
        db.commit()

        # Recalculate order totals
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            if order_items:
                new_subtotal = sum(item.total_price for item in order_items)
                new_tax_amount = new_subtotal * Decimal('0.10')
                new_total_amount = new_subtotal + new_tax_amount + order.shipping_amount - order.discount_amount

                order.subtotal = new_subtotal
                order.tax_amount = new_tax_amount
                order.total_amount = new_total_amount
            else:
                # No items left, set totals to zero
                order.subtotal = Decimal('0')
                order.tax_amount = Decimal('0')
                order.total_amount = order.shipping_amount - order.discount_amount

            db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove order item: internal server error"
        )


# User endpoints - authenticated users can manage their own orders

@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new order.

    **Authenticated endpoint** - Creates a new order with the provided information
    and order items. Order number and pricing calculations are handled automatically.

    - **order_items**: List of products to order (at least one required)
    - **customer_email**: Customer's email address
    - **customer_phone**: Optional customer phone number
    - **shipping_***: Shipping address information (all required)
    - **billing_***: Billing address information (all required)
    - **notes**: Optional customer notes

    The order will be associated with the authenticated user.
    Pricing is calculated based on current product prices unless specified.
    """
    return create_order_service(db, order_data, current_user)


@router.get("/", response_model=List[OrderSummary])
async def list_user_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List current user's orders.

    **Authenticated endpoint** - Returns a paginated list of orders belonging
    to the authenticated user with summary information.

    - **skip**: Number of orders to skip (for pagination)
    - **limit**: Maximum number of orders to return (max 100)

    Only returns orders belonging to the authenticated user.
    """
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return orders


@router.get("/{order_id}", response_model=OrderRead)
async def get_user_order(
    order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's order by ID.

    **Authenticated endpoint** - Retrieves complete order information for the
    specified order ID. Users can only access their own orders.

    - **order_id**: UUID of the order to retrieve

    Returns detailed order information including all order items.
    """
    order = get_order_by_id(db, order_id)

    # Check if user owns this order
    if not check_resource_ownership(current_user, order.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: insufficient permissions"
        )

    return order


@router.patch("/{order_id}", response_model=OrderRead)
async def update_user_order(
    order_id: UUID,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update/cancel user's order.

    **Authenticated endpoint** - Allows users to update their own order information
    or cancel orders. Users can only modify their own orders.

    - **order_id**: UUID of the order to update
    - **status**: New order status (e.g., "cancelled")
    - **customer_email**: Updated customer email
    - **customer_phone**: Updated customer phone
    - **shipping_***: Updated shipping address fields
    - **billing_***: Updated billing address fields
    - **notes**: Updated customer notes

    Users cannot modify order items through this endpoint.
    """
    order = get_order_by_id(db, order_id)

    # Check if user owns this order
    if not check_resource_ownership(current_user, order.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: insufficient permissions"
        )

    return update_order_service(db, order, order_update)


# Order item management endpoints

@router.post("/{order_id}/items", response_model=OrderItemRead, status_code=status.HTTP_201_CREATED)
async def add_order_item(
    order_id: UUID,
    item_data: OrderItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add item to order.

    **Authenticated endpoint** - Adds a new item to an existing order.
    Users can only modify their own orders.

    - **order_id**: UUID of the order to add item to
    - **product_id**: UUID of the product to add
    - **quantity**: Quantity of the product
    - **unit_price**: Optional price override (uses product price if not specified)
    - **product_name**: Product name for historical record
    - **product_sku**: Product SKU for historical record
    - **product_description**: Optional product description

    Order totals are recalculated automatically.
    """
    order = get_order_by_id(db, order_id)

    # Check if user owns this order
    if not check_resource_ownership(current_user, order.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: insufficient permissions"
        )

    return create_order_item_service(db, order, item_data)


@router.patch("/{order_id}/items/{item_id}", response_model=OrderItemRead)
async def update_order_item(
    order_id: UUID,
    item_id: UUID,
    item_update: OrderItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update order item.

    **Authenticated endpoint** - Updates an existing order item.
    Users can only modify items in their own orders.

    - **order_id**: UUID of the order containing the item
    - **item_id**: UUID of the order item to update
    - **quantity**: New quantity for the item
    - **unit_price**: New unit price for the item

    Order totals are recalculated automatically.
    """
    order = get_order_by_id(db, order_id)
    order_item = get_order_item_by_id(db, item_id)

    # Verify the order item belongs to the specified order
    if order_item.order_id != order.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order item does not belong to the specified order"
        )

    # Check if user owns this order
    if not check_resource_ownership(current_user, order.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: insufficient permissions"
        )

    return update_order_item_service(db, order_item, item_update)


@router.delete("/{order_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_order_item(
    order_id: UUID,
    item_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove item from order.

    **Authenticated endpoint** - Removes an item from an existing order.
    Users can only modify items in their own orders.

    - **order_id**: UUID of the order containing the item
    - **item_id**: UUID of the order item to remove

    Order totals are recalculated automatically.
    Returns 204 No Content on successful removal.
    """
    order = get_order_by_id(db, order_id)
    order_item = get_order_item_by_id(db, item_id)

    # Verify the order item belongs to the specified order
    if order_item.order_id != order.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order item does not belong to the specified order"
        )

    # Check if user owns this order
    if not check_resource_ownership(current_user, order.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: insufficient permissions"
        )

    delete_order_item_service(db, order_item)


# Admin-only endpoints

@router.get("/all", response_model=List[OrderSummary])
async def list_all_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    List all orders in the system.

    **Admin only endpoint** - Returns a paginated list of all orders with
    summary information.

    - **skip**: Number of orders to skip (for pagination)
    - **limit**: Maximum number of orders to return (max 100)

    Requires admin role for access.
    """
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders


@router.get("/admin/{order_id}", response_model=OrderRead)
async def get_any_order(
    order_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get any order by ID.

    **Admin only endpoint** - Retrieves complete order information for any
    order in the system, regardless of ownership.

    - **order_id**: UUID of the order to retrieve

    Requires admin role for access.
    """
    return get_order_by_id(db, order_id)


@router.patch("/admin/{order_id}", response_model=OrderRead)
async def update_any_order(
    order_id: UUID,
    order_update: OrderUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Update/cancel any order.

    **Admin only endpoint** - Allows administrators to update any order
    information including internal notes and status changes.

    - **order_id**: UUID of the order to update
    - **status**: New order status
    - **payment_status**: New payment status
    - **internal_notes**: Internal admin notes
    - **customer_***: Customer information updates
    - **shipping_***: Shipping address updates
    - **billing_***: Billing address updates

    Requires admin role for access.
    """
    order = get_order_by_id(db, order_id)
    return update_order_service(db, order, order_update)
