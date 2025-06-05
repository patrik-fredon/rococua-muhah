"""
JWT token creation and validation utilities.

This module handles JWT token generation, validation, and decoding for user authentication.
Uses python-jose for JWT operations with configurable expiration and security settings.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.core.config import settings


class TokenError(Exception):
    """Custom exception for token-related errors."""
    pass


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token with user data and expiration.

    Args:
        data: Dictionary containing user data to encode in the token
        expires_delta: Optional custom expiration delta, defaults to config setting

    Returns:
        Encoded JWT token string

    Raises:
        TokenError: If token creation fails

    Example:
        >>> token_data = {"sub": str(user.id), "email": user.email}
        >>> token = create_access_token(token_data)
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        return encoded_jwt
    except Exception as e:
        raise TokenError(f"Failed to create access token: {str(e)}")


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        Dictionary containing the decoded token payload

    Raises:
        HTTPException: If token is invalid, expired, or malformed

    Example:
        >>> payload = verify_token(token)
        >>> user_id = payload.get("sub")
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token without raising exceptions.

    This is useful for cases where you want to handle invalid tokens gracefully
    without raising HTTP exceptions.

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary containing the decoded token payload, or None if invalid

    Example:
        >>> payload = decode_token(token)
        >>> if payload:
        ...     user_id = payload.get("sub")
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


def extract_user_id_from_token(token: str) -> Optional[UUID]:
    """
    Extract user ID from a JWT token.

    Args:
        token: JWT token string

    Returns:
        UUID of the user if valid, None otherwise

    Example:
        >>> user_id = extract_user_id_from_token(token)
        >>> if user_id:
        ...     # Process authenticated user
    """
    payload = decode_token(token)
    if not payload:
        return None

    user_id_str = payload.get("sub")
    if not user_id_str:
        return None

    try:
        return UUID(user_id_str)
    except (ValueError, TypeError):
        return None


def create_token_response(user_id: UUID, email: str, roles: list = None) -> Dict[str, Any]:
    """
    Create a standardized token response with user information.

    Args:
        user_id: User's unique identifier
        email: User's email address
        roles: List of user's role names

    Returns:
        Dictionary containing access token and token metadata

    Example:
        >>> response = create_token_response(user.id, user.email, ["user", "admin"])
        >>> # Returns: {"access_token": "...", "token_type": "bearer", "user": {...}}
    """
    if roles is None:
        roles = []

    token_data = {
        "sub": str(user_id),
        "email": email,
        "roles": roles
    }

    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,  # Convert to seconds
        "user": {
            "id": str(user_id),
            "email": email,
            "roles": roles
        }
    }
