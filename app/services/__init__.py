"""
Services package for business logic and data access layer.

This package provides service classes that implement business logic,
data validation, and CRUD operations for all entities in the application.
"""

from .base import CRUDBase
from .user_service import UserService, user_service
from .product_service import ProductService, product_service

__all__ = [
    "CRUDBase",
    "UserService",
    "user_service",
    "ProductService",
    "product_service",
]
