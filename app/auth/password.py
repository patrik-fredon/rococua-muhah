"""
Password hashing and verification utilities.

This module provides secure password hashing using bcrypt with configurable rounds
and salt generation. Uses passlib for robust password handling.
"""

from passlib.context import CryptContext
from typing import Optional


# Configure password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: The plain text password to hash

    Returns:
        The bcrypt hashed password string

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The stored hashed password to check against

    Returns:
        True if the password matches, False otherwise

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def needs_update(hashed_password: str) -> bool:
    """
    Check if a hashed password needs to be updated (re-hashed).

    This is useful when the hashing algorithm or cost factor changes,
    allowing for gradual migration of existing password hashes.

    Args:
        hashed_password: The stored hashed password to check

    Returns:
        True if the password hash should be updated, False otherwise
    """
    return pwd_context.needs_update(hashed_password)
