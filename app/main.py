import os
import sys
import time
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Add the parent directory to Python path to resolve 'app' module imports
# This ensures 'from app.api import api_router' works when running from project root
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=settings.log_file if settings.log_file else None,
)
logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if settings.https_only:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url}")

        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.4f}s")

        response.headers["X-Process-Time"] = str(process_time)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting FastAPI Dashboard application...")

    if settings.websocket_enabled:
        # Import here to avoid circular imports
        from app.api.ws import manager

        # Initialize Redis connection for WebSocket manager
        await manager.initialize_redis()
        logger.info("WebSocket manager initialized")

    yield

    # Shutdown
    logger.info("Shutting down FastAPI Dashboard application...")

    if settings.websocket_enabled:
        from app.api.ws import manager

        # Close Redis connection
        if manager.redis_client:
            await manager.redis_client.aclose()
            logger.info("Redis connection closed")


# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    description="Modern FastAPI + Next.js Dashboard System with CRUD operations, real-time updates, and secure authentication",
    debug=settings.debug,
    docs_url="/docs" if settings.swagger_ui_enabled else None,
    redoc_url="/redoc" if settings.swagger_ui_enabled else None,
    lifespan=lifespan,
)

# Add security middleware
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*"],  # Configure for your domain
    )

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add request logging in development
if settings.is_development:
    app.add_middleware(LoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with consistent error format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time(),
            "path": str(request.url.path),
        },
    )


# Include API routes with versioned prefix
app.include_router(api_router, prefix=settings.api_v1_prefix)

# Mount static files for admin dashboard (if exists)
dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard")
if os.path.exists(dashboard_path):
    app.mount(
        "/dashboard", StaticFiles(directory=dashboard_path, html=True), name="dashboard"
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Health status with system information
    """
    return {
        "status": "healthy",
        "service": "fastapi_dashboard",
        "version": settings.project_version,
        "environment": settings.environment,
        "timestamp": time.time(),
        "features": {
            "websocket": settings.websocket_enabled,
            "swagger_ui": settings.swagger_ui_enabled,
            "rate_limiting": settings.rate_limit_enabled,
        },
    }


@app.get("/")
async def read_root():
    """
    Root endpoint with API information and available endpoints.

    Returns:
        dict: API information and available services
    """
    endpoints = {
        "health": "/health",
        "api_docs": "/docs" if settings.swagger_ui_enabled else None,
        "api_version": settings.api_v1_prefix,
    }

    if settings.websocket_enabled:
        endpoints["websocket_endpoints"] = {
            "orders": f"{settings.api_v1_prefix}/ws/orders/{{order_id}}",
            "products": f"{settings.api_v1_prefix}/ws/products",
            "health": f"{settings.api_v1_prefix}/ws/health",
        }

    return {
        "message": "FastAPI Dashboard System",
        "version": settings.project_version,
        "environment": settings.environment,
        "endpoints": endpoints,
        "timestamp": time.time(),
    }


# Production optimizations
if settings.is_production:
    # Disable debug mode
    app.debug = False

    # Set up production logging
    if not settings.log_file:
        # Use structured logging for production
        logging.basicConfig(
            level=logging.WARNING,
            format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
            datefmt="%Y-%m-%d %H:%M:%S",
        )
