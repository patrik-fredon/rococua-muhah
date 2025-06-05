"""
Role Pydantic schemas for request/response serialization.

This module defines schemas for Role model operations including
creation, updates, and responses with proper validation and documentation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class RoleBase(BaseModel):
    """
    Base Role schema with common fields for creation and updates.

    Contains role information including name, display name, and description
    that can be provided during role creation or modification operations.
    """
    name: str = Field(..., min_length=2, max_length=50, description="Unique role name (lowercase, no spaces)")
    display_name: str = Field(..., min_length=2, max_length=100, description="Human-readable role name")
    description: Optional[str] = Field(None, description="Role description and purpose")
    is_active: bool = Field(True, description="Whether the role is active and can be assigned")

    @validator('name')
    def validate_name(cls, v):
        """Validate role name format."""
        if not v.islower():
            raise ValueError('Role name must be lowercase')
        if ' ' in v:
            raise ValueError('Role name cannot contain spaces')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Role name must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @validator('display_name')
    def validate_display_name(cls, v):
        """Validate display name is not empty after stripping."""
        if not v.strip():
            raise ValueError('Display name cannot be empty')
        return v.strip()


class RoleCreate(RoleBase):
    """
    Schema for creating a new role.

    Inherits all fields from RoleBase. All fields are required except
    description which is optional.
    """
    pass


class RoleUpdate(BaseModel):
    """
    Schema for updating an existing role.

    All fields are optional to allow partial updates. Name uniqueness
    will be validated at the database level.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="Unique role name (lowercase, no spaces)")
    display_name: Optional[str] = Field(None, min_length=2, max_length=100, description="Human-readable role name")
    description: Optional[str] = Field(None, description="Role description and purpose")
    is_active: Optional[bool] = Field(None, description="Whether the role is active and can be assigned")

    @validator('name')
    def validate_name(cls, v):
        """Validate role name format."""
        if v is not None:
            if not v.islower():
                raise ValueError('Role name must be lowercase')
            if ' ' in v:
                raise ValueError('Role name cannot contain spaces')
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Role name must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @validator('display_name')
    def validate_display_name(cls, v):
        """Validate display name is not empty after stripping."""
        if v is not None:
            if not v.strip():
                raise ValueError('Display name cannot be empty')
            return v.strip()
        return v


class RoleRead(RoleBase):
    """
    Schema for reading role data in API responses.

    Includes all role information with read-only fields like ID and timestamps.
    Used for returning role data in API responses.
    """
    id: UUID = Field(..., description="Role's unique identifier")
    created_at: datetime = Field(..., description="Role creation timestamp")
    updated_at: datetime = Field(..., description="Last role update timestamp")

    class Config:
        from_attributes = True


class RoleInDB(RoleRead):
    """
    Schema representing role data as stored in database.

    Currently identical to RoleRead as roles don't have sensitive fields.
    Kept for consistency and future extensibility.
    """
    pass
