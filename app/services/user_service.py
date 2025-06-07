"""
User service layer implementing CRUD operations and business logic.

This module provides user-specific operations extending the base CRUD service
with authentication, role management, and user-specific business rules.
"""

from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import CRUDBase
from app.auth.password import get_password_hash, verify_password


class UserService(CRUDBase[User, UserCreate, UserUpdate]):
    """
    User service with authentication and user management operations.
    """

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            db: Database session
            email: User's email address

        Returns:
            User instance if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            db: Database session
            username: User's username

        Returns:
            User instance if found, None otherwise
        """
        return db.query(User).filter(User.username == username).first()

    def get_by_email_or_username(
        self, db: Session, *, identifier: str
    ) -> Optional[User]:
        """
        Get user by email or username.

        Args:
            db: Database session
            identifier: Email address or username

        Returns:
            User instance if found, None otherwise
        """
        return (
            db.query(User)
            .filter((User.email == identifier) | (User.username == identifier))
            .first()
        )

    def create_user(self, db: Session, *, user_create: UserCreate) -> User:
        """
        Create a new user with hashed password.

        Args:
            db: Database session
            user_create: User creation data

        Returns:
            Created user instance

        Raises:
            HTTPException: 400 if email or username already exists
        """
        # Check if email already exists
        if self.get_by_email(db, email=user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already registered",
            )

        # Check if username already exists
        if self.get_by_username(db, username=user_create.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

        # Hash password and create user
        hashed_password = get_password_hash(user_create.password)
        user_data = user_create.dict(exclude={"password"})
        user_data["hashed_password"] = hashed_password

        try:
            db_user = User(**user_data)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}",
            )

    def authenticate(
        self, db: Session, *, identifier: str, password: str
    ) -> Optional[User]:
        """
        Authenticate user with email/username and password.

        Args:
            db: Database session
            identifier: Email address or username
            password: Plain text password

        Returns:
            User instance if authentication successful, None otherwise
        """
        user = self.get_by_email_or_username(db, identifier=identifier)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def activate_user(self, db: Session, *, user: User) -> User:
        """
        Activate a user account.

        Args:
            db: Database session
            user: User instance to activate

        Returns:
            Updated user instance
        """
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user

    def deactivate_user(self, db: Session, *, user: User) -> User:
        """
        Deactivate a user account.

        Args:
            db: Database session
            user: User instance to deactivate

        Returns:
            Updated user instance
        """
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    def verify_user(self, db: Session, *, user: User) -> User:
        """
        Mark user as email verified.

        Args:
            db: Database session
            user: User instance to verify

        Returns:
            Updated user instance
        """
        user.is_verified = True
        db.commit()
        db.refresh(user)
        return user

    def change_password(self, db: Session, *, user: User, new_password: str) -> User:
        """
        Change user's password.

        Args:
            db: Database session
            user: User instance
            new_password: New plain text password

        Returns:
            Updated user instance
        """
        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password
        db.commit()
        db.refresh(user)
        return user

    def get_active_users(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Get list of active users.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active users
        """
        return self.get_multi(db, skip=skip, limit=limit, filters={"is_active": True})

    def get_verified_users(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Get list of verified users.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of verified users
        """
        return self.get_multi(db, skip=skip, limit=limit, filters={"is_verified": True})


# Create service instance
user_service = UserService(User)
