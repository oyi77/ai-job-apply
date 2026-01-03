"""Database configuration for the AI Job Application Assistant."""

import os
import warnings
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, StaticPool
from sqlalchemy import exc as sa_exc
from ..config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Suppress SQLAlchemy connection pool warnings in development
# These warnings occur when connections are garbage collected,
# but with proper context managers, connections are properly closed
warnings.filterwarnings("ignore", category=sa_exc.SAWarning, message=".*non-checked-in connection.*")


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
        
        # Check for database type preference
        db_type = os.getenv("DB_TYPE", "sqlite").lower()
        
        if db_type == "mysql":
            # MySQL configuration
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "3306")
            db_name = os.getenv("DB_NAME", "ai_job_assistant")
            db_user = os.getenv("DB_USER", "root")
            db_password = os.getenv("DB_PASSWORD", "")
            
            if db_password:
                return f"mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            else:
                return f"mysql+aiomysql://{db_user}@{db_host}:{db_port}/{db_name}"
        
        elif db_type == "postgresql":
            # PostgreSQL configuration (if explicitly requested)
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "ai_job_assistant")
            db_user = os.getenv("DB_USER", "postgres")
            db_password = os.getenv("DB_PASSWORD", "")
            
            if db_password:
                return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            else:
                return f"postgresql+asyncpg://{db_user}@{db_host}:{db_port}/{db_name}"
        
        else:
            # Default to SQLite (file-based)
            db_path = os.getenv("DB_PATH", "ai_job_assistant.db")
            return f"sqlite+aiosqlite:///{db_path}"
    
    def get_test_database_url(self) -> str:
        """Get the test database URL."""
        # For testing, use a separate SQLite file to ensure isolation and persistence during the test
        return "sqlite+aiosqlite:///test_ai_job_assistant.db"
    
    async def initialize(self, test_mode: bool = False) -> None:
        """Initialize database connection."""
        if self._initialized:
            return
        
        try:
            if test_mode:
                database_url = self.get_test_database_url()
                logger.info("Initializing test database (SQLite file-based)")
            else:
                database_url = self.get_database_url()
                logger.info(f"Initializing database: {database_url}")
            
            # Create async engine
            connect_args = {}
            poolclass = None

            if database_url.startswith("sqlite"):
                # For SQLite, we need to ensure the directory exists for file-based dbs
                if not ":memory:" in database_url:
                    db_path = database_url.replace("sqlite+aiosqlite:///", "")
                    if "/" in db_path:
                        os.makedirs(os.path.dirname(db_path), exist_ok=True)
                
                # For SQLite with aiosqlite:
                # - Use StaticPool for in-memory databases (shared cache)
                # - Use NullPool for file-based databases (avoids connection pool issues)
                poolclass = StaticPool if ":memory:" in database_url else NullPool
                # aiosqlite requires check_same_thread=False for async operations
                connect_args["check_same_thread"] = False
                # Set timeout for SQLite operations
                connect_args["timeout"] = 20.0

            elif test_mode:
                # For non-SQLite tests, still use NullPool
                poolclass = NullPool

            # Build engine kwargs
            engine_kwargs = {
                "echo": config.DEBUG,  # Log SQL queries in debug mode
                "poolclass": poolclass,
                "connect_args": connect_args,
            }
            
            # For SQLite with aiosqlite, ensure proper async handling
            if database_url.startswith("sqlite"):
                # Ensure poolclass is set for SQLite
                if poolclass is None:
                    poolclass = NullPool
                    engine_kwargs["poolclass"] = poolclass
                # aiosqlite requires check_same_thread=False
                if "check_same_thread" not in connect_args:
                    connect_args["check_same_thread"] = False
            
            # Add pool settings only for non-NullPool (connection pooling enabled)
            if poolclass is not None and poolclass != NullPool:
                engine_kwargs["pool_pre_ping"] = True  # Verify connections before using
                engine_kwargs["pool_recycle"] = 3600  # Recycle connections after 1 hour
            
            # Create async engine with proper configuration
            # For SQLite, ensure we're using the correct driver
            if database_url.startswith("sqlite"):
                # Ensure aiosqlite is available
                try:
                    import aiosqlite
                except ImportError:
                    logger.error("aiosqlite is required for SQLite async operations. Install it with: pip install aiosqlite")
                    raise ImportError("aiosqlite is not installed. Please install it with: pip install aiosqlite")
            
            self.engine = create_async_engine(
                database_url,
                **engine_kwargs
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
    
    def get_session(self):
        """Get a new database session context manager.
        
        Usage:
            async with database_config.get_session() as session:
                # use session
        """
        if not self._initialized or self.async_session_maker is None:
            raise RuntimeError(
                "Database not initialized. Call database_config.initialize() first. "
                "This should happen automatically during application startup."
            )
        
        return self.async_session_maker()
    
    async def get_session_async(self) -> AsyncSession:
        """Get a new database session (deprecated - use get_session() as context manager instead).
        
        WARNING: Sessions returned by this method MUST be explicitly closed.
        Prefer using get_session() as a context manager instead.
        """
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
    """Dependency function to get database session.
    
    This is a FastAPI dependency that yields a session.
    The session is automatically closed when the request completes.
    """
    async with database_config.get_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        # Context manager automatically closes the session


async def get_database():
    """Async generator to get database session (for compatibility).
    
    This yields a session that is automatically closed when the generator completes.
    """
    async with database_config.get_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        # Context manager automatically closes the session


async def init_database() -> None:
    """Initialize database on application startup."""
    await database_config.initialize()
    await database_config.create_tables()


async def close_database() -> None:
    """Close database on application shutdown."""
    await database_config.close()
