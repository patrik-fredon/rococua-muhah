"""
Role management API routes.

This module provides RESTful API endpoints for role administration,
including CRUD operations with proper admin-only access control.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate
from app.models.role import Role
from app.models.user import User
from app.auth import require_role

router = APIRouter(prefix="/roles", tags=["roles"])


def get_role_by_id(db: Session, role_id: UUID) -> Role:
    """
    Get a role by ID.

    Args:
        db: Database session
        role_id: Role's unique identifier

    Returns:
        Role object if found

    Raises:
        HTTPException: If role not found
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


def create_role_service(db: Session, role_create: RoleCreate) -> Role:
    """
    Create a new role.

    Args:
        db: Database session
        role_create: Role creation data

    Returns:
        Created role object

    Raises:
        HTTPException: If role creation fails
    """
    try:
        role = Role(
            name=role_create.name,
            display_name=role_create.display_name,
            description=role_create.description,
            is_active=role_create.is_active
        )

        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    except IntegrityError as e:
        db.rollback()
        if "name" in str(e.orig).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create role: constraint violation"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create role: internal server error"
        )


def update_role_service(db: Session, role: Role, role_update: RoleUpdate) -> Role:
    """
    Update an existing role.

    Args:
        db: Database session
        role: Role object to update
        role_update: Role update data

    Returns:
        Updated role object

    Raises:
        HTTPException: If role update fails
    """
    try:
        # Update role fields
        update_data = role_update.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(role, field, value)

        db.commit()
        db.refresh(role)
        return role

    except IntegrityError as e:
        db.rollback()
        if "name" in str(e.orig).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update role: constraint violation"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role: internal server error"
        )


def delete_role_service(db: Session, role: Role) -> None:
    """
    Delete a role.

    Args:
        db: Database session
        role: Role object to delete

    Raises:
        HTTPException: If role deletion fails
    """
    try:
        # Check if role is assigned to any users
        if role.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete role '{role.name}': still assigned to {len(role.users)} user(s)"
            )

        db.delete(role)
        db.commit()

    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete role: internal server error"
        )


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Create a new role.

    **Admin only endpoint** - Creates a new role with the provided information.
    Role names must be unique and follow the naming conventions.

    - **name**: Unique role name (lowercase, alphanumeric with hyphens/underscores)
    - **display_name**: Human-readable role name
    - **description**: Optional role description
    - **is_active**: Whether the role is active (default: true)

    Requires admin role for access.
    """
    return create_role_service(db, role_data)


@router.get("/", response_model=List[RoleRead])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    List all roles in the system.

    **Admin only endpoint** - Returns a paginated list of all roles with their
    complete information including timestamps and user assignments.

    - **skip**: Number of roles to skip (for pagination)
    - **limit**: Maximum number of roles to return (max 100)

    Requires admin role for access.
    """
    roles = db.query(Role).offset(skip).limit(limit).all()
    return roles


@router.get("/{role_id}", response_model=RoleRead)
async def get_role_by_id_endpoint(
    role_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get role by ID.

    **Admin only endpoint** - Retrieves complete role information for the
    specified role ID, including timestamps and user assignments.

    - **role_id**: UUID of the role to retrieve

    Requires admin role for access.
    """
    return get_role_by_id(db, role_id)


@router.patch("/{role_id}", response_model=RoleRead)
async def update_role_by_id(
    role_id: UUID,
    role_update: RoleUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Update role by ID.

    **Admin only endpoint** - Allows administrators to update role information.
    All fields are optional for partial updates. Role name uniqueness is enforced.

    - **role_id**: UUID of the role to update
    - **name**: New unique role name (lowercase, alphanumeric with hyphens/underscores)
    - **display_name**: New human-readable role name
    - **description**: Updated role description
    - **is_active**: Role active status

    Requires admin role for access.
    """
    role = get_role_by_id(db, role_id)
    return update_role_service(db, role, role_update)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role_by_id(
    role_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Delete role by ID.

    **Admin only endpoint** - Deletes the specified role. Roles that are
    currently assigned to users cannot be deleted and will return an error.

    - **role_id**: UUID of the role to delete

    Returns 204 No Content on successful deletion.
    Requires admin role for access.
    """
    role = get_role_by_id(db, role_id)
    delete_role_service(db, role)
