#!/usr/bin/env python3
"""
Seed script to create a default test user for development.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database.config import DatabaseConfig
from src.services.service_registry import service_registry
from src.models.user import UserRegister
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Default test user credentials
DEFAULT_EMAIL = "test@example.com"
DEFAULT_PASSWORD = "Test123!@#"
DEFAULT_NAME = "Test User"


async def seed_default_user():
    """Create a default test user if it doesn't exist."""
    try:
        logger.info("Seeding default user...")
        
        # Initialize database
        db_config = DatabaseConfig()
        await db_config.initialize()
        
        # Get auth service
        auth_service = await service_registry.get_auth_service()
        
        # Check if user already exists
        try:
            user_repo = auth_service._repository
            existing_user = await user_repo.get_by_email(DEFAULT_EMAIL)
            
            if existing_user:
                logger.info(f"User {DEFAULT_EMAIL} already exists. Skipping creation.")
                print(f"✅ User already exists: {DEFAULT_EMAIL}")
                print(f"   Password: {DEFAULT_PASSWORD}")
                await db_config.close()
                return
        except Exception as e:
            logger.warning(f"Could not check for existing user: {e}")
        
        # Create default user
        registration = UserRegister(
            email=DEFAULT_EMAIL,
            password=DEFAULT_PASSWORD,
            name=DEFAULT_NAME
        )
        
        try:
            response = await auth_service.register_user(registration)
            logger.info(f"Default user created successfully: {DEFAULT_EMAIL}")
            print("✅ Default user created successfully!")
            print(f"   Email: {DEFAULT_EMAIL}")
            print(f"   Password: {DEFAULT_PASSWORD}")
            print(f"   Name: {DEFAULT_NAME}")
        except ValueError as e:
            if "already exists" in str(e).lower() or "email" in str(e).lower():
                logger.info(f"User {DEFAULT_EMAIL} already exists.")
                print(f"✅ User already exists: {DEFAULT_EMAIL}")
                print(f"   Password: {DEFAULT_PASSWORD}")
            else:
                raise
        
        await db_config.close()
        
    except Exception as e:
        logger.error(f"Error seeding default user: {e}", exc_info=True)
        print(f"❌ Error creating default user: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    print("🌱 Seeding default test user...")
    print()
    
    try:
        asyncio.run(seed_default_user())
        print()
        print("🎯 You can now login with the credentials above")
    except Exception as e:
        print(f"❌ Failed to seed default user: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

