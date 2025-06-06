"""
Authentication-specific schemas.

This module contains Pydantic schemas for authentication-related requests
and responses, including login, token validation, and password operations.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator


class LoginRequest(BaseModel):
    """
    Schema for user login requests.

    Used with OAuth2 password flow for user authentication.
    Supports both email and username as identifiers.
    """
    username: str = Field(..., description="User's email address or username")
    password: str = Field(..., description="User's password")

    @validator('username')
    def validate_username(cls, v):
        """Validate username is not empty."""
        if not v.strip():
            raise ValueError('Username/email cannot be empty')
        return v.strip().lower()


class TokenResponse(BaseModel):
    """
    Schema for token response after successful authentication.

    Returns access token with metadata and user information.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: dict = Field(..., description="User information")


class TokenData(BaseModel):
    """
    Schema for token payload data.

    Used internally for token creation and validation.
    """
    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User's email address")
    roles: List[str] = Field(default_factory=list, description="User's roles")
    exp: Optional[int] = Field(None, description="Expiration timestamp")


class PasswordChangeRequest(BaseModel):
    """
    Schema for password change requests.

    Requires current password for security verification.
    """
    current_password: str = Field(..., description="Current password")
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


class PasswordResetRequest(BaseModel):
    """
    Schema for password reset requests.

    Used to initiate password reset flow.
    """
    email: str = Field(..., description="Email address for password reset")

    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v.lower().strip()


class PasswordResetConfirm(BaseModel):
    """
    Schema for password reset confirmation.

    Used to complete password reset with token.
    """
    token: str = Field(..., description="Password reset token")
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


class EmailVerificationRequest(BaseModel):
    """
    Schema for email verification requests.

    Used to request email verification.
    """
    email: str = Field(..., description="Email address to verify")

    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v.lower().strip()


class EmailVerificationConfirm(BaseModel):
    """
    Schema for email verification confirmation.

    Used to confirm email verification with token.
    """
    token: str = Field(..., description="Email verification token")


class RoleAssignmentRequest(BaseModel):
    """
    Schema for role assignment requests.

    Used by administrators to assign roles to users.
    """
    user_id: str = Field(..., description="User ID to assign role to")
    role_name: str = Field(..., description="Role name to assign")

    @validator('role_name')
    def validate_role_name(cls, v):
        """Validate role name format."""
        if not v.strip():
            raise ValueError('Role name cannot be empty')
        return v.strip().lower()


class UserStatusUpdate(BaseModel):
    """
    Schema for updating user account status.

    Used by administrators to activate/deactivate or verify users.
    """
    is_active: Optional[bool] = Field(None, description="Whether user account is active")
    is_verified: Optional[bool] = Field(None, description="Whether user email is verified")


class AuthResponse(BaseModel):
    """
    Generic authentication response schema.

    Used for standardized success/error responses.
    """
    success: bool = Field(..., description="Whether operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Additional response data")


class RefreshTokenRequest(BaseModel):
    """
    Schema for refresh token requests.

    Used for token refresh operations (if implemented).
    """
    refresh_token: str = Field(..., description="Refresh token")


class LogoutRequest(BaseModel):
    """
    Schema for logout requests.

    Used for token invalidation (if implemented).
    """
    token: Optional[str] = Field(None, description="Token to invalidate")
    all_devices: bool = Field(False, description="Logout from all devices")
