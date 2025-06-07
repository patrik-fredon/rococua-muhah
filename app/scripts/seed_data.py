#!/usr/bin/env python3
"""
Database seeding script for FastAPI Dashboard System

This script creates initial data for development and testing purposes.
"""

import sys
from pathlib import Path

# Add the parent directory to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.models.user import User
from app.models.role import Role
from app.models.product import Product
from app.auth.password import get_password_hash


def create_roles(db: Session):
    """Create default roles"""
    roles = [
        {"name": "admin", "description": "Administrator with full access"},
        {"name": "manager", "description": "Manager with limited admin access"},
        {"name": "user", "description": "Regular user with basic access"},
    ]

    created_roles = {}
    for role_data in roles:
        # Check if role already exists
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            db.commit()
            db.refresh(role)
            created_roles[role.name] = role
            print(f"✅ Created role: {role.name}")
        else:
            created_roles[existing_role.name] = existing_role
            print(f"⚠️  Role already exists: {existing_role.name}")

    return created_roles


def create_users(db: Session, roles: dict):
    """Create default users"""
    users = [
        {
            "email": "admin@example.com",
            "full_name": "Admin User",
            "hashed_password": get_password_hash("password"),
            "is_active": True,
            "role_id": roles["admin"].id,
        },
        {
            "email": "manager@example.com",
            "full_name": "Manager User",
            "hashed_password": get_password_hash("password"),
            "is_active": True,
            "role_id": roles["manager"].id,
        },
        {
            "email": "user@example.com",
            "full_name": "Regular User",
            "hashed_password": get_password_hash("password"),
            "is_active": True,
            "role_id": roles["user"].id,
        },
    ]

    created_users = []
    for user_data in users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            created_users.append(user)
            print(f"✅ Created user: {user.email}")
        else:
            created_users.append(existing_user)
            print(f"⚠️  User already exists: {existing_user.email}")

    return created_users


def create_products(db: Session):
    """Create sample products"""
    products = [
        {
            "name": "Premium Dashboard Pro",
            "description": "Advanced dashboard solution with premium features",
            "price": 99.99,
            "stock_quantity": 50,
            "is_active": True,
        },
        {
            "name": "Basic Dashboard",
            "description": "Simple dashboard for small businesses",
            "price": 29.99,
            "stock_quantity": 100,
            "is_active": True,
        },
        {
            "name": "Enterprise Dashboard",
            "description": "Full-featured enterprise solution",
            "price": 299.99,
            "stock_quantity": 25,
            "is_active": True,
        },
        {
            "name": "Analytics Module",
            "description": "Advanced analytics and reporting module",
            "price": 49.99,
            "stock_quantity": 75,
            "is_active": True,
        },
        {
            "name": "API Access License",
            "description": "Unlimited API access for developers",
            "price": 19.99,
            "stock_quantity": 200,
            "is_active": True,
        },
    ]

    created_products = []
    for product_data in products:
        # Check if product already exists
        existing_product = (
            db.query(Product).filter(Product.name == product_data["name"]).first()
        )
        if not existing_product:
            product = Product(**product_data)
            db.add(product)
            db.commit()
            db.refresh(product)
            created_products.append(product)
            print(f"✅ Created product: {product.name}")
        else:
            created_products.append(existing_product)
            print(f"⚠️  Product already exists: {existing_product.name}")

    return created_products


def seed_database():
    """Main seeding function"""
    print("🌱 Starting database seeding...")

    # Create all tables
    from app.core.database import Base

    Base.metadata.create_all(bind=engine)

    # Get database session
    db = next(get_db())

    try:
        # Create roles
        print("\n📝 Creating roles...")
        roles = create_roles(db)

        # Create users
        print("\n👥 Creating users...")
        users = create_users(db, roles)

        # Create products
        print("\n📦 Creating products...")
        products = create_products(db)

        print(f"\n✅ Database seeding completed successfully!")
        print(f"   - Created {len(roles)} roles")
        print(f"   - Created {len(users)} users")
        print(f"   - Created {len(products)} products")

        print("\n🔑 Default login credentials:")
        print("   Admin: admin@example.com / password")
        print("   Manager: manager@example.com / password")
        print("   User: user@example.com / password")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
