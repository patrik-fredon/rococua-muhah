"""
Base CRUD service classes for implementing consistent data access patterns.

This module provides generic base classes for implementing CRUD operations
with consistent error handling, validation, and database management.
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD service class with default methods to Create, Read, Update, Delete (CRUD).

    This class provides consistent patterns for database operations across all entities.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD service with SQLAlchemy model.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model instance if found, None otherwise
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_or_404(self, db: Session, id: UUID) -> ModelType:
        """
        Get a single record by ID or raise 404 error.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model instance

        Raises:
            HTTPException: 404 if record not found
        """
        instance = self.get(db, id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found",
            )
        return instance

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and optional filters.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters to apply

        Returns:
            List of model instances
        """
        query = db.query(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            obj_in: Pydantic schema with creation data

        Returns:
            Created model instance

        Raises:
            HTTPException: 400 for validation errors, 500 for other errors
        """
        try:
            obj_data = obj_in.dict()
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create {self.model.__name__}: {str(e.orig)}",
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create {self.model.__name__}: {str(e)}",
            )

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Pydantic schema with update data

        Returns:
            Updated model instance

        Raises:
            HTTPException: 400 for validation errors, 500 for other errors
        """
        try:
            update_data = obj_in.dict(exclude_unset=True)

            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update {self.model.__name__}: {str(e.orig)}",
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update {self.model.__name__}: {str(e)}",
            )

    def delete(self, db: Session, *, db_obj: ModelType) -> ModelType:
        """
        Delete a record.

        Args:
            db: Database session
            db_obj: Model instance to delete

        Returns:
            Deleted model instance

        Raises:
            HTTPException: 400 for constraint violations, 500 for other errors
        """
        try:
            db.delete(db_obj)
            db.commit()
            return db_obj
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete {self.model.__name__}: {str(e.orig)}",
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete {self.model.__name__}: {str(e)}",
            )

    def count(self, db: Session, *, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters.

        Args:
            db: Database session
            filters: Optional filters to apply

        Returns:
            Count of matching records
        """
        query = db.query(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        return query.count()

    def exists(self, db: Session, id: UUID) -> bool:
        """
        Check if a record exists by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            True if record exists, False otherwise
        """
        return db.query(self.model).filter(self.model.id == id).first() is not None
