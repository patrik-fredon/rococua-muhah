from fastapi import FastAPI
from app.api import api_router
from app.core.config import Settings

# Load settings
settings = Settings()

app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    description="RESTful API with user management and authentication"
)

# Include API routes with versioned prefix
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def read_root():
    return {"message": "Hello World", "docs": "/docs", "api_version": "v1"}
