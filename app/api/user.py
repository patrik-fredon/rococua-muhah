"""
User management API routes.

This module provides RESTful API endpoints for user registration, authentication,
profile management, and administrative user operations with proper role-based access control.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.auth.schemas import (
    LoginRequest,
    TokenResponse,
    PasswordChangeRequest,
    UserStatusUpdate,
    AuthResponse,
)
from app.auth.jwt import create_token_response
from app.auth import get_current_active_user, require_role
from app.models.user import User
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register_new_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Creates a new user with the provided information and returns an access token.
    The user will be assigned the default "user" role and marked as unverified.

    - **email**: Valid email address (must be unique)
    - **username**: Unique username (3-100 characters, alphanumeric + hyphens/underscores)
    - **password**: Strong password (min 8 chars, mixed case, numbers)
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    - **phone**: Optional phone number
    - **address**: Optional address

    Returns access token and user information upon successful registration.
    """
    user = user_service.create_user(db, user_create=user_data)

    # Create token response
    roles = [role.name for role in user.roles] if user.roles else ["user"]
    return create_token_response(user.id, user.email, roles)


@router.post("/login", response_model=TokenResponse)
async def login_user_account(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.

    Validates user credentials and returns a JWT access token for API authentication.
    The username field accepts either email address or username.

    - **username**: Email address or username
    - **password**: User's password

    Updates the user's last login timestamp upon successful authentication.
    """
    user = user_service.authenticate(
        db, identifier=login_data.username, password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Create token response
    roles = [role.name for role in user.roles] if user.roles else ["user"]
    return create_token_response(user.id, user.email, roles)


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current authenticated user's profile.

    Returns the complete profile information for the currently authenticated user,
    including assigned roles and account status.

    Requires valid authentication token.
    """
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update current authenticated user's profile.

    Allows users to update their own profile information. All fields are optional
    for partial updates. Email and username uniqueness is enforced.

    - **email**: New email address (must be unique)
    - **username**: New username (must be unique)
    - **first_name**: Updated first name
    - **last_name**: Updated last name
    - **phone**: Updated phone number
    - **address**: Updated address

    Users cannot modify their own account status (is_active, is_verified).
    """
    # Update user fields
    update_data = user_update.dict(
        exclude_unset=True, exclude={"is_active", "is_verified"}
    )

    for field, value in update_data.items():
        setattr(current_user, field, value)

    try:
        db.commit()
        db.refresh(current_user)
        return current_user
    except Exception as e:
        db.rollback()
        if "email" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already in use",
            )
        elif "username" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile",
            )


@router.post("/change-password", response_model=AuthResponse)
async def change_user_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Change current user's password.

    Allows authenticated users to change their password by providing their current
    password for verification and a new strong password.

    - **current_password**: Current password for verification
    - **new_password**: New strong password (min 8 chars, mixed case, numbers)

    Returns success confirmation upon password change.
    """
    # Verify current password
    authenticated_user = user_service.authenticate(
        db, identifier=current_user.email, password=password_data.current_password
    )
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    user_service.change_password(
        db, user=current_user, new_password=password_data.new_password
    )

    return AuthResponse(success=True, message="Password changed successfully")


# Admin-only endpoints below


@router.get("/", response_model=List[UserRead])
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    List all users in the system.

    **Admin only endpoint** - Returns a paginated list of all users with their
    complete profile information and assigned roles.

    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return (max 100)

    Requires admin role for access.
    """
    return user_service.get_multi(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id_endpoint(
    user_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Get user by ID.

    **Admin only endpoint** - Retrieves complete user information for the
    specified user ID, including profile data and assigned roles.

    - **user_id**: UUID of the user to retrieve

    Requires admin role for access.
    """
    return user_service.get_or_404(db, user_id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user_by_id(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Update user by ID.

    **Admin only endpoint** - Allows administrators to update any user's profile
    information and account status. All fields are optional for partial updates.

    - **user_id**: UUID of the user to update
    - **email**: New email address (must be unique)
    - **username**: New username (must be unique)
    - **first_name**: Updated first name
    - **last_name**: Updated last name
    - **phone**: Updated phone number
    - **address**: Updated address
    - **is_active**: Account active status
    - **is_verified**: Email verification status

    Requires admin role for access.
    """
    user = user_service.get_or_404(db, user_id)
    return user_service.update(db, db_obj=user, obj_in=user_update)


@router.post("/{user_id}/status", response_model=AuthResponse)
async def update_user_status(
    user_id: UUID,
    status_update: UserStatusUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Update user account status.

    **Admin only endpoint** - Allows administrators to activate/deactivate user
    accounts or update email verification status.

    - **user_id**: UUID of the user to update
    - **is_active**: Set account active status (true/false)
    - **is_verified**: Set email verification status (true/false)

    At least one status field must be provided.
    Requires admin role for access.
    """
    user = user_service.get_or_404(db, user_id)

    # Check if at least one status field is provided
    if status_update.is_active is None and status_update.is_verified is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one status field must be provided",
        )

    # Update status fields
    if status_update.is_active is not None:
        if status_update.is_active:
            user_service.activate_user(db, user=user)
        else:
            user_service.deactivate_user(db, user=user)

    if status_update.is_verified is not None:
        if status_update.is_verified:
            user_service.verify_user(db, user=user)
        else:
            user.is_verified = False
            db.commit()

    # Prepare response message
    status_changes = []
    if status_update.is_active is not None:
        status_changes.append(f"active: {status_update.is_active}")
    if status_update.is_verified is not None:
        status_changes.append(f"verified: {status_update.is_verified}")

    message = f"User status updated - {', '.join(status_changes)}"

    return AuthResponse(success=True, message=message, data={"user_id": str(user_id)})
