"""Database configuration for the AI Job Application Assistant."""

import os
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from ..config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class DatabaseConfig:
    """Database configuration manager."""
    
    def __init__(self):
        """Initialize database configuration."""
        self.engine = None
        self.async_session_maker = None
        self._initialized = False
    
    def get_database_url(self) -> str:
        """Get the database URL from environment or use default."""
        # Check for environment variable first
        database_url = os.getenv("DATABASE_URL")
        
        if database_url:
            logger.info("Using DATABASE_URL from environment")
            return database_url
        
        # Check for individual database configuration
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "ai_job_assistant")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "")
        
        if db_password:
            return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            return f"postgresql+asyncpg://{db_user}@{db_host}:{db_port}/{db_name}"
    
    def get_test_database_url(self) -> str:
        """Get the test database URL."""
        # For testing, use SQLite in memory
        return "sqlite+aiosqlite:///:memory:"
    
    async def initialize(self, test_mode: bool = False) -> None:
        """Initialize database connection."""
        if self._initialized:
            return
        
        try:
            if test_mode:
                database_url = self.get_test_database_url()
                logger.info("Initializing test database (SQLite in-memory)")
            else:
                database_url = self.get_database_url()
                logger.info(f"Initializing database: {database_url}")
            
            # Create async engine
            self.engine = create_async_engine(
                database_url,
                echo=config.DEBUG,  # Log SQL queries in debug mode
                poolclass=NullPool if test_mode else None,  # No connection pooling for tests
                future=True,
            )
            
            # Create async session maker
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            self._initialized = True
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise
    
    async def get_session(self) -> AsyncSession:
        """Get a new database session."""
        if not self._initialized:
            await self.initialize()
        
        return self.async_session_maker()
    
    async def close(self) -> None:
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False
            logger.info("Database connections closed")
    
    async def create_tables(self) -> None:
        """Create all database tables."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}", exc_info=True)
            raise
    
    async def drop_tables(self) -> None:
        """Drop all database tables (for testing)."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}", exc_info=True)
            raise


# Global database configuration instance
database_config = DatabaseConfig()


async def get_db_session() -> AsyncSession:
    """Dependency function to get database session."""
    async with database_config.get_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database() -> None:
    """Initialize database on application startup."""
    await database_config.initialize()
    await database_config.create_tables()


async def close_database() -> None:
    """Close database on application shutdown."""
    await database_config.close()
