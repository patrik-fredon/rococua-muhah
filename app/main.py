from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import api_router
from app.core.config import Settings
import os

# Load settings
settings = Settings()

app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    description="RESTful API with user management, authentication, and real-time updates"
)

# Add CORS middleware for WebSocket support
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with versioned prefix
app.include_router(api_router, prefix=settings.api_v1_prefix)

# Mount static files for admin dashboard
dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard")
if os.path.exists(dashboard_path):
    app.mount(
        "/dashboard",
        StaticFiles(directory=dashboard_path, html=True),
        name="dashboard"
    )


@app.get("/dashboard/health")
async def dashboard_health_check():
    """
    Health check endpoint for the admin dashboard.

    Returns:
        dict: Simple JSON status indicating the dashboard service is healthy
    """
    return {
        "status": "healthy",
        "service": "admin_dashboard",
        "message": "Dashboard service is operational"
    }


@app.get("/")
def read_root():
    return {
        "message": "Hello World",
        "docs": "/docs",
        "api_version": "v1",
        "websocket_endpoints": {
            "orders": f"{settings.api_v1_prefix}/ws/orders/{{order_id}}",
            "products": f"{settings.api_v1_prefix}/ws/products",
            "health": f"{settings.api_v1_prefix}/ws/health"
        }
    }


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Import here to avoid circular imports
    from app.api.ws import manager

    # Initialize Redis connection for WebSocket manager
    await manager.initialize_redis()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown."""
    # Import here to avoid circular imports
    from app.api.ws import manager

    # Close Redis connection
    if manager.redis_client:
        await manager.redis_client.aclose()
