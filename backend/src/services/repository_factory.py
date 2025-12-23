"""Repository factory for creating repositories with database sessions."""

from typing import Optional, Callable, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.config import database_config
from loguru import logger


class RepositoryFactory:
    """Factory for creating repositories with database sessions."""
    
    def __init__(self):
        """Initialize the repository factory."""
        self.logger = logger.bind(module="RepositoryFactory")
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the factory and database."""
        if self._initialized:
            return
        
        try:
            if not database_config._initialized:
                await database_config.initialize()
                await database_config.create_tables()
            self._initialized = True
            self.logger.info("Repository factory initialized")
        except Exception as e:
            self.logger.warning(f"Database initialization failed: {e}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Check if database is available."""
        return self._initialized and database_config._initialized
    
    async def create_repository(self, repository_class: type, *args, **kwargs) -> Optional[Any]:
        """Create a repository instance with a database session."""
        if not self.is_available():
            return None
        
        try:
            session = await database_config.get_session()
            return repository_class(session, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error creating repository: {e}", exc_info=True)
            return None


# Global repository factory instance
repository_factory = RepositoryFactory()

