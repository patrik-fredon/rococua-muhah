"""
API routes package.

This package organizes all API route modules and provides centralized router registration
for the FastAPI application.
"""

from fastapi import APIRouter
from .user import router as user_router
from .role import router as role_router
from .product import router as product_router
from .order import router as order_router
from .ws import router as ws_router

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(user_router)
api_router.include_router(role_router)
api_router.include_router(product_router)
api_router.include_router(order_router)
api_router.include_router(ws_router)

__all__ = ["api_router"]
