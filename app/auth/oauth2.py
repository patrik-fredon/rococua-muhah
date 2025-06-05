"""
OAuth2 password flow implementation for FastAPI.

This module provides OAuth2 password bearer token authentication scheme
and dependency injection for protecting API endpoints.
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.auth.jwt import verify_token, extract_user_id_from_token


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",  # URL where clients can get tokens
    scheme_name="JWT"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    This dependency extracts and validates the JWT token, then retrieves
    the corresponding user from the database. Used to protect endpoints
    that require authentication.

    Args:
        token: JWT token from Authorization header
        db: Database session dependency

    Returns:
        User object of the authenticated user

    Raises:
        HTTPException: If token is invalid or user not found

    Usage:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.email}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify and decode the token
        payload = verify_token(token)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        # Convert string ID to UUID
        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError):
            raise credentials_exception

    except HTTPException:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current active user.

    This is an additional layer that explicitly checks if the user is active.
    Useful for endpoints that require not just authentication but also
    an active account status.

    Args:
        current_user: User from get_current_user dependency

    Returns:
        Active user object

    Raises:
        HTTPException: If user account is not active

    Usage:
        @app.get("/active-only")
        async def active_route(user: User = Depends(get_current_active_user)):
            return {"message": "Active user endpoint"}
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to get the current verified user.

    Requires the user to be both active and verified. Useful for
    endpoints that require email verification or account validation.

    Args:
        current_user: User from get_current_active_user dependency

    Returns:
        Verified user object

    Raises:
        HTTPException: If user account is not verified

    Usage:
        @app.get("/verified-only")
        async def verified_route(user: User = Depends(get_current_verified_user)):
            return {"message": "Verified user endpoint"}
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not verified"
        )
    return current_user


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally get the current user.

    This dependency allows for optional authentication - it returns
    the user if a valid token is provided, or None if no token or
    invalid token is provided. Useful for endpoints that work for
    both authenticated and anonymous users.

    Args:
        token: Optional JWT token from Authorization header
        db: Database session dependency

    Returns:
        User object if authenticated, None otherwise

    Usage:
        @app.get("/optional-auth")
        async def optional_route(user: Optional[User] = Depends(get_optional_current_user)):
            if user:
                return {"message": f"Hello {user.email}"}
            return {"message": "Hello anonymous user"}
    """
    if not token:
        return None

    try:
        user_id = extract_user_id_from_token(token)
        if not user_id:
            return None

        user = db.query(User).filter(User.id == user_id).first()
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None
