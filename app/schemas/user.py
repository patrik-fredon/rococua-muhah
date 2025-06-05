"""
User Pydantic schemas for request/response serialization.

This module defines schemas for User model operations including
creation, updates, and responses with proper validation and documentation.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

from .role import RoleRead


class UserBase(BaseModel):
    """
    Base User schema with common fields for creation and updates.

    Contains user profile information and contact details that can be
    provided during user creation or modification operations.
    """
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=100, description="Unique username")
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
    phone: Optional[str] = Field(None, max_length=20, description="User's phone number")
    address: Optional[str] = Field(None, description="User's address")
    is_active: bool = Field(True, description="Whether the user account is active")
    is_verified: bool = Field(False, description="Whether the user's email is verified")

    @validator('username')
    def validate_username(cls, v):
        """Validate username contains only alphanumeric characters and underscores."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        """Basic phone number validation."""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Phone number must contain only digits and common separators')
        return v


class UserCreate(UserBase):
    """
    Schema for creating a new user.

    Extends UserBase with required password field for user registration.
    Password is required and will be hashed before storage.
    """
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.

    All fields are optional to allow partial updates. Email and username
    uniqueness will be validated at the database level.
    """
    email: Optional[EmailStr] = Field(None, description="User's email address")
    username: Optional[str] = Field(None, min_length=3, max_length=100, description="Unique username")
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
    phone: Optional[str] = Field(None, max_length=20, description="User's phone number")
    address: Optional[str] = Field(None, description="User's address")
    is_active: Optional[bool] = Field(None, description="Whether the user account is active")
    is_verified: Optional[bool] = Field(None, description="Whether the user's email is verified")

    @validator('username')
    def validate_username(cls, v):
        """Validate username contains only alphanumeric characters and underscores."""
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        """Basic phone number validation."""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Phone number must contain only digits and common separators')
        return v


class UserRead(UserBase):
    """
    Schema for reading user data in API responses.

    Includes all user information with read-only fields like ID and timestamps.
    Used for returning user data in API responses with related roles.
    """
    id: UUID = Field(..., description="User's unique identifier")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="Last user update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    roles: List[RoleRead] = Field(default_factory=list, description="User's assigned roles")

    class Config:
        from_attributes = True


class UserInDB(UserRead):
    """
    Schema representing user data as stored in database.

    Includes sensitive information like hashed password that should
    not be exposed in API responses. Used internally by services.
    """
    hashed_password: str = Field(..., description="User's hashed password")


class UserPasswordUpdate(BaseModel):
    """
    Schema for updating user password.

    Requires both current and new password for security.
    Used in password change operations.
    """
    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")

    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
