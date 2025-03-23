from typing import List, Optional
import logging

from tortoise import Tortoise
from tortoise.exceptions import OperationalError

from app.core.config import settings
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


async def init_db():
    """
    Initialize the database with required models and create initial admin user.
    """
    try:
        # Register all models
        await Tortoise.init(
            db_url=settings.DATABASE_URL,
            modules={"models": ["app.models.user", "app.models.ride", "app.models.payment"]}
        )
        
        # Generate the schema
        await Tortoise.generate_schemas()
        
        # Create admin user if it doesn't exist
        await create_initial_admin()
        
        logger.info("Database initialization complete")
    except OperationalError as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def create_initial_admin():
    """
    Create an initial admin user if no admin exists.
    """
    # Check if admin exists
    admin = await User.filter(role=UserRole.ADMIN).first()
    
    if not admin:
        logger.info("Creating initial admin user")
        admin = User(
            email="admin@example.com",
            full_name="Admin User",
            phone_number="1234567890",
            role=UserRole.ADMIN,
            is_active=True
        )
        admin.hashed_password = User.get_password_hash("adminpassword")
        await admin.save()
        logger.info(f"Admin user created with email: {admin.email}")
    else:
        logger.info("Admin user already exists")


async def close_db_connections():
    """
    Close database connections.
    """
    await Tortoise.close_connections() 