import secrets
from typing import Optional, List, Union
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Provides secure defaults and validation for production deployment.
    """

    # Database configuration
    database_url: str = Field(
        default="sqlite:///./app.db", description="Database connection URL"
    )

    # Security
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT token signing",
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="JWT token expiration time in minutes"
    )

    # Redis configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching and WebSocket scaling",
    )

    # API configuration
    api_v1_prefix: str = Field(default="/api/v1", description="API version prefix")
    project_name: str = Field(default="FastAPI Dashboard", description="Project name")
    project_version: str = Field(default="1.0.0", description="Project version")

    # CORS settings
    backend_cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins",
    )

    # Environment
    environment: str = Field(
        default="development",
        description="Environment mode: development, production, testing",
    )
    debug: bool = Field(default=True, description="Enable debug mode")

    # Security headers and settings
    secure_cookies: bool = Field(
        default=False, description="Enable secure cookies in production"
    )
    https_only: bool = Field(default=False, description="Force HTTPS in production")

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(
        default=60, description="Rate limit requests per minute"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(
        default=None, description="Log file path (None for stdout)"
    )

    # Performance
    workers: int = Field(default=1, description="Number of worker processes")
    max_connections: int = Field(
        default=1000, description="Maximum concurrent connections"
    )

    # Optional third-party integrations
    sentry_dsn: Optional[str] = Field(
        default=None, description="Sentry DSN for error tracking"
    )
    email_backend: Optional[str] = Field(
        default=None, description="Email backend configuration"
    )

    # Feature flags
    websocket_enabled: bool = Field(
        default=True, description="Enable WebSocket support"
    )
    swagger_ui_enabled: bool = Field(
        default=True, description="Enable Swagger UI documentation"
    )

    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from environment variable"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment setting"""
        allowed_envs = ["development", "production", "testing"]
        if v.lower() not in allowed_envs:
            raise ValueError(f"Environment must be one of: {allowed_envs}")
        return v.lower()

    @validator("secret_key")
    def validate_secret_key(cls, v: str, values: dict) -> str:
        """Ensure secret key is secure in production"""
        if values.get("environment") == "production":
            if v == "default-secret-key-for-development":
                raise ValueError(
                    "Default secret key is not allowed in production. "
                    "Set SECRET_KEY environment variable."
                )
            if len(v) < 32:
                raise ValueError(
                    "Secret key must be at least 32 characters in production"
                )
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.environment == "testing"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Allow field aliases for environment variables
        fields = {"backend_cors_origins": {"env": "BACKEND_CORS_ORIGINS"}}


# Global settings instance
settings = Settings()
