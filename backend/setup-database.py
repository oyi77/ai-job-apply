#!/usr/bin/env python3
"""
Simple database setup script for AI Job Application Assistant.
Uses SQLite by default for easy development setup.
"""

import asyncio
import os
from pathlib import Path

# Add src to path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database.config import DatabaseConfig, init_database
from src.database.models import Base
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def setup_database():
    """Set up the database with tables."""
    try:
        logger.info("Setting up database...")

        # Initialize database configuration
        db_config = DatabaseConfig()

        # Use SQLite by default
        os.environ.setdefault("DB_TYPE", "sqlite")
        os.environ.setdefault("DB_PATH", "ai_job_assistant.db")

        # Initialize database
        await db_config.initialize()

        # Create all tables
        async with db_config.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database setup completed successfully!")
        logger.info(
            f"Database file: {os.environ.get('DB_PATH', 'ai_job_assistant.db')}"
        )

        # Test connection
        async with db_config.get_session() as session:
            from sqlalchemy import text

            result = await session.execute(text("SELECT 1"))
            logger.info("Database connection test: SUCCESS")

        # Close database engine to release connections
        await db_config.close()

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        # Ensure cleanup even on error
        try:
            await db_config.close()
        except:
            pass
        raise


def main():
    """Main entry point."""
    print("[*] Setting up AI Job Application Assistant Database...")
    print("[*] Using SQLite for simple development setup")
    print()

    try:
        asyncio.run(setup_database())
        print("[OK] Database setup completed successfully!")
        print("[*] You can now run the application with: python main.py")
    except Exception as e:
        print(f"[ERROR] Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
