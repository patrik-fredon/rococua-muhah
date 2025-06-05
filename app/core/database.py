from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from .config import settings


# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    # SQLite specific settings - remove echo in production
    echo=settings.debug,
    # For SQLite, we need to enable check_same_thread=False to work with FastAPI
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class for declarative models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    This function creates a new database session for each request
    and ensures it's properly closed after the request is completed.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/users/")
        def read_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    Create all database tables defined by SQLAlchemy models.

    This function should be called during application startup
    to ensure all required tables exist in the database.

    Note:
        In production, consider using Alembic migrations instead
        of creating tables programmatically.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """
    Drop all database tables defined by SQLAlchemy models.

    This function is primarily useful for testing and development.
    Use with caution in production environments.

    Warning:
        This will permanently delete all data in the database.
    """
    Base.metadata.drop_all(bind=engine)
