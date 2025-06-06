"""
Authentication and authorization package.

This package provides comprehensive authentication and authorization functionality
for the FastAPI application including:

- Password hashing and verification (passlib/bcrypt)
- JWT token creation and validation (python-jose)
- OAuth2 password flow implementation
- Role-based access control (RBAC)
- User registration and login services
- Authentication middleware and dependencies

Usage:
    from app.auth import password, jwt, oauth2, permissions, services
    from app.auth.oauth2 import get_current_user
    from app.auth.permissions import require_role
    from app.auth.services import register_user, login_user
"""

# Password utilities
from .password import (
    hash_password,
    verify_password,
    needs_update,
)

# JWT token utilities
from .jwt import (
    create_access_token,
    verify_token,
    decode_token,
    extract_user_id_from_token,
    create_token_response,
    TokenError,
)

# OAuth2 dependencies
from .oauth2 import (
    oauth2_scheme,
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    get_optional_current_user,
)

# Permission and role utilities
from .permissions import (
    has_role,
    has_any_role,
    has_all_roles,
    has_minimum_role_level,
    get_user_roles,
    get_user_max_role_level,
    require_role,
    require_any_role,
    require_minimum_role,
    check_resource_ownership,
    require_ownership_or_role,
    PermissionError,
    ROLE_HIERARCHY,
)

# Authentication services
from .services import (
    authenticate_user,
    login_user,
    register_user,
    change_password,
    get_user_by_email,
    get_user_by_username,
    get_user_by_id,
    activate_user,
    deactivate_user,
    verify_user_email,
    assign_role_to_user,
    remove_role_from_user,
    AuthenticationError,
    RegistrationError,
)

# Authentication schemas
from .schemas import (
    LoginRequest,
    TokenResponse,
    TokenData,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    RoleAssignmentRequest,
    UserStatusUpdate,
    AuthResponse,
    RefreshTokenRequest,
    LogoutRequest,
)

__all__ = [
    # Password utilities
    "hash_password",
    "verify_password",
    "needs_update",

    # JWT utilities
    "create_access_token",
    "verify_token",
    "decode_token",
    "extract_user_id_from_token",
    "create_token_response",
    "TokenError",

    # OAuth2 dependencies
    "oauth2_scheme",
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "get_optional_current_user",

    # Permission utilities
    "has_role",
    "has_any_role",
    "has_all_roles",
    "has_minimum_role_level",
    "get_user_roles",
    "get_user_max_role_level",
    "require_role",
    "require_any_role",
    "require_minimum_role",
    "check_resource_ownership",
    "require_ownership_or_role",
    "PermissionError",
    "ROLE_HIERARCHY",

    # Service functions
    "authenticate_user",
    "login_user",
    "register_user",
    "change_password",
    "get_user_by_email",
    "get_user_by_username",
    "get_user_by_id",
    "activate_user",
    "deactivate_user",
    "verify_user_email",
    "assign_role_to_user",
    "remove_role_from_user",
    "AuthenticationError",
    "RegistrationError",

    # Schemas
    "LoginRequest",
    "TokenResponse",
    "TokenData",
    "PasswordChangeRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "EmailVerificationRequest",
    "EmailVerificationConfirm",
    "RoleAssignmentRequest",
    "UserStatusUpdate",
    "AuthResponse",
    "RefreshTokenRequest",
    "LogoutRequest",
]
