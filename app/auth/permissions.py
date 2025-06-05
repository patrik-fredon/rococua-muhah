"""
Role-based access control (RBAC) utilities.

This module provides decorators and functions for implementing role-based
access control in FastAPI applications. Supports role checking, permission
validation, and hierarchical role structures.
"""

from typing import List, Set, Optional, Callable, Any
from functools import wraps

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role
from app.auth.oauth2 import get_current_active_user


class PermissionError(Exception):
    """Custom exception for permission-related errors."""
    pass


# Define role hierarchy (higher roles inherit permissions from lower ones)
ROLE_HIERARCHY = {
    "super_admin": 100,
    "admin": 80,
    "manager": 60,
    "staff": 40,
    "user": 20,
    "guest": 10,
}


def get_role_level(role_name: str) -> int:
    """
    Get the hierarchical level of a role.

    Args:
        role_name: Name of the role

    Returns:
        Integer representing the role's level in hierarchy
    """
    return ROLE_HIERARCHY.get(role_name.lower(), 0)


def has_role(user: User, required_role: str) -> bool:
    """
    Check if a user has a specific role.

    Args:
        user: User object to check
        required_role: Name of the required role

    Returns:
        True if user has the role, False otherwise

    Example:
        >>> if has_role(user, "admin"):
        ...     # User has admin role
    """
    if not user or not user.roles:
        return False

    user_roles = {role.name.lower() for role in user.roles if role.is_active}
    return required_role.lower() in user_roles


def has_any_role(user: User, required_roles: List[str]) -> bool:
    """
    Check if a user has any of the specified roles.

    Args:
        user: User object to check
        required_roles: List of role names (user needs at least one)

    Returns:
        True if user has any of the roles, False otherwise

    Example:
        >>> if has_any_role(user, ["admin", "manager"]):
        ...     # User has either admin or manager role
    """
    if not user or not user.roles:
        return False

    user_roles = {role.name.lower() for role in user.roles if role.is_active}
    required_roles_lower = {role.lower() for role in required_roles}

    return bool(user_roles.intersection(required_roles_lower))


def has_all_roles(user: User, required_roles: List[str]) -> bool:
    """
    Check if a user has all of the specified roles.

    Args:
        user: User object to check
        required_roles: List of role names (user needs all of them)

    Returns:
        True if user has all roles, False otherwise

    Example:
        >>> if has_all_roles(user, ["user", "verified"]):
        ...     # User has both user and verified roles
    """
    if not user or not user.roles:
        return False

    user_roles = {role.name.lower() for role in user.roles if role.is_active}
    required_roles_lower = {role.lower() for role in required_roles}

    return required_roles_lower.issubset(user_roles)


def has_minimum_role_level(user: User, minimum_role: str) -> bool:
    """
    Check if a user has a role with at least the specified hierarchy level.

    This allows for hierarchical role checking where higher roles
    automatically have permissions of lower roles.

    Args:
        user: User object to check
        minimum_role: Minimum required role name

    Returns:
        True if user has sufficient role level, False otherwise

    Example:
        >>> if has_minimum_role_level(user, "manager"):
        ...     # User has manager, admin, or super_admin role
    """
    if not user or not user.roles:
        return False

    minimum_level = get_role_level(minimum_role)
    user_max_level = max(
        (get_role_level(role.name) for role in user.roles if role.is_active),
        default=0
    )

    return user_max_level >= minimum_level


def get_user_roles(user: User) -> Set[str]:
    """
    Get all active role names for a user.

    Args:
        user: User object

    Returns:
        Set of active role names

    Example:
        >>> roles = get_user_roles(user)
        >>> # Returns: {"user", "admin"}
    """
    if not user or not user.roles:
        return set()

    return {role.name for role in user.roles if role.is_active}


def get_user_max_role_level(user: User) -> int:
    """
    Get the highest role level for a user.

    Args:
        user: User object

    Returns:
        Integer representing the highest role level
    """
    if not user or not user.roles:
        return 0

    return max(
        (get_role_level(role.name) for role in user.roles if role.is_active),
        default=0
    )


# Dependency functions for FastAPI route protection

def require_role(required_role: str):
    """
    FastAPI dependency factory for role-based access control.

    Args:
        required_role: Name of the required role

    Returns:
        FastAPI dependency function

    Usage:
        @app.get("/admin-only", dependencies=[Depends(require_role("admin"))])
        async def admin_endpoint():
            return {"message": "Admin access granted"}
    """
    def role_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if not has_role(current_user, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role}"
            )
        return current_user

    return role_dependency


def require_any_role(required_roles: List[str]):
    """
    FastAPI dependency factory for multiple role access control.

    Args:
        required_roles: List of acceptable role names

    Returns:
        FastAPI dependency function

    Usage:
        @app.get("/staff-area", dependencies=[Depends(require_any_role(["admin", "staff"]))])
        async def staff_endpoint():
            return {"message": "Staff access granted"}
    """
    def role_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if not has_any_role(current_user, required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {', '.join(required_roles)}"
            )
        return current_user

    return role_dependency


def require_minimum_role(minimum_role: str):
    """
    FastAPI dependency factory for hierarchical role access control.

    Args:
        minimum_role: Minimum required role name

    Returns:
        FastAPI dependency function

    Usage:
        @app.get("/manager-plus", dependencies=[Depends(require_minimum_role("manager"))])
        async def manager_endpoint():
            return {"message": "Manager or higher access granted"}
    """
    def role_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if not has_minimum_role_level(current_user, minimum_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required minimum role: {minimum_role}"
            )
        return current_user

    return role_dependency


def check_resource_ownership(user: User, resource_user_id: Any) -> bool:
    """
    Check if a user owns a specific resource.

    This is useful for endpoints where users should only access
    their own resources unless they have elevated permissions.

    Args:
        user: Current user
        resource_user_id: User ID associated with the resource

    Returns:
        True if user owns the resource or has admin privileges

    Example:
        >>> if check_resource_ownership(current_user, order.user_id):
        ...     # User can access this order
    """
    # Convert resource_user_id to string for comparison
    resource_user_str = str(resource_user_id)
    current_user_str = str(user.id)

    # User owns the resource
    if current_user_str == resource_user_str:
        return True

    # User has admin privileges
    if has_minimum_role_level(user, "admin"):
        return True

    return False


def require_ownership_or_role(resource_user_id: Any, fallback_role: str = "admin"):
    """
    FastAPI dependency factory for resource ownership or role-based access.

    Args:
        resource_user_id: User ID associated with the resource
        fallback_role: Role that bypasses ownership requirement

    Returns:
        FastAPI dependency function

    Usage:
        @app.get("/orders/{order_id}")
        async def get_order(
            order_id: UUID,
            order: Order = Depends(get_order_by_id),
            current_user: User = Depends(require_ownership_or_role(order.user_id))
        ):
            return order
    """
    def ownership_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if not check_resource_ownership(current_user, resource_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient permissions"
            )
        return current_user

    return ownership_dependency
