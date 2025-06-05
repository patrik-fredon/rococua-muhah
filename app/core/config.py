from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Database configuration
    database_url: str = "sqlite:///./app.db"

    # Security
    secret_key: str = "default-secret-key-for-development"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Redis configuration
    redis_url: str = "redis://localhost:6379/0"

    # API configuration
    api_v1_prefix: str = "/api/v1"
    project_name: str = "FastAPI Project"
    project_version: str = "1.0.0"

    # CORS settings
    backend_cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]

    # Environment
    environment: str = "development"
    debug: bool = True

    # Optional third-party integrations
    sentry_dsn: Optional[str] = None
    email_backend: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
