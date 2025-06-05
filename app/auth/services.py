"""
Authentication service functions.

This module provides core authentication services including user registration,
login, password validation, and token management. These functions handle the
business logic for user authentication workflows.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserInDB
from app.auth.password import hash_password, verify_password, needs_update
from app.auth.jwt import create_token_response


class AuthenticationError(Exception):
    """Custom exception for authentication-related errors."""
    pass


class RegistrationError(Exception):
    """Custom exception for user registration errors."""
    pass


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password.

    Args:
        db: Database session
        email: User's email address
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise

    Example:
        >>> user = authenticate_user(db, "user@example.com", "password123")
        >>> if user:
        ...     # Authentication successful
    """
    # Get user by email
    user = db.query(User).filter(User.email == email.lower()).first()

    if not user:
        return None

    # Verify password
    if not verify_password(password, user.hashed_password):
        return None

    # Check if user is active
    if not user.is_active:
        return None

    return user


def login_user(db: Session, email: str, password: str) -> Dict[str, Any]:
    """
    Login a user and return token response.

    Args:
        db: Database session
        email: User's email address
        password: Plain text password

    Returns:
        Dictionary containing access token and user information

    Raises:
        HTTPException: If authentication fails

    Example:
        >>> token_data = login_user(db, "user@example.com", "password123")
        >>> access_token = token_data["access_token"]
    """
    user = authenticate_user(db, email, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login timestamp
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Check if password needs update (rehashing)
    if needs_update(user.hashed_password):
        user.hashed_password = hash_password(password)
        db.commit()

    # Get user roles
    role_names = [role.name for role in user.roles if role.is_active]

    # Create token response
    return create_token_response(user.id, user.email, role_names)


def register_user(db: Session, user_create: UserCreate) -> Dict[str, Any]:
    """
    Register a new user account.

    Args:
        db: Database session
        user_create: User creation data

    Returns:
        Dictionary containing access token and user information

    Raises:
        HTTPException: If registration fails

    Example:
        >>> user_data = UserCreate(email="new@example.com", password="password123", ...)
        >>> token_data = register_user(db, user_data)
    """
    try:
        # Hash the password
        hashed_password = hash_password(user_create.password)

        # Create user object
        user = User(
            email=user_create.email.lower(),
            username=user_create.username,
            hashed_password=hashed_password,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            phone=user_create.phone,
            address=user_create.address,
            is_active=True,
            is_verified=False  # Email verification required
        )

        # Add default user role
        default_role = db.query(Role).filter(Role.name == "user").first()
        if default_role:
            user.roles.append(default_role)

        db.add(user)
        db.commit()
        db.refresh(user)

        # Get user roles
        role_names = [role.name for role in user.roles if role.is_active]

        # Create token response
        return create_token_response(user.id, user.email, role_names)

    except IntegrityError as e:
        db.rollback()

        # Check which constraint was violated
        error_msg = str(e.orig).lower()
        if "email" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already registered"
            )
        elif "username" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed: user already exists"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed: internal server error"
        )


def change_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
    """
    Change a user's password.

    Args:
        db: Database session
        user: User object
        current_password: Current plain text password
        new_password: New plain text password

    Returns:
        True if password change successful

    Raises:
        HTTPException: If current password is incorrect

    Example:
        >>> success = change_password(db, user, "old_pass", "new_pass")
    """
    # Verify current password
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Hash and update new password
    user.hashed_password = hash_password(new_password)
    db.commit()

    return True


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email address.

    Args:
        db: Database session
        email: Email address to search for

    Returns:
        User object if found, None otherwise

    Example:
        >>> user = get_user_by_email(db, "user@example.com")
    """
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get a user by username.

    Args:
        db: Database session
        username: Username to search for

    Returns:
        User object if found, None otherwise

    Example:
        >>> user = get_user_by_username(db, "johndoe")
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """
    Get a user by ID.

    Args:
        db: Database session
        user_id: User's unique identifier

    Returns:
        User object if found, None otherwise

    Example:
        >>> user = get_user_by_id(db, user_uuid)
    """
    return db.query(User).filter(User.id == user_id).first()


def activate_user(db: Session, user: User) -> User:
    """
    Activate a user account.

    Args:
        db: Database session
        user: User object to activate

    Returns:
        Updated user object

    Example:
        >>> user = activate_user(db, user)
    """
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user: User) -> User:
    """
    Deactivate a user account.

    Args:
        db: Database session
        user: User object to deactivate

    Returns:
        Updated user object

    Example:
        >>> user = deactivate_user(db, user)
    """
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


def verify_user_email(db: Session, user: User) -> User:
    """
    Mark a user's email as verified.

    Args:
        db: Database session
        user: User object to verify

    Returns:
        Updated user object

    Example:
        >>> user = verify_user_email(db, user)
    """
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user


def assign_role_to_user(db: Session, user: User, role_name: str) -> bool:
    """
    Assign a role to a user.

    Args:
        db: Database session
        user: User object
        role_name: Name of the role to assign

    Returns:
        True if role assigned successfully, False if role not found

    Example:
        >>> success = assign_role_to_user(db, user, "admin")
    """
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        return False

    # Check if user already has this role
    if role in user.roles:
        return True

    user.roles.append(role)
    db.commit()
    return True


def remove_role_from_user(db: Session, user: User, role_name: str) -> bool:
    """
    Remove a role from a user.

    Args:
        db: Database session
        user: User object
        role_name: Name of the role to remove

    Returns:
        True if role removed successfully, False if role not found

    Example:
        >>> success = remove_role_from_user(db, user, "admin")
    """
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        return False

    # Check if user has this role
    if role not in user.roles:
        return True

    user.roles.remove(role)
    db.commit()
    return True
