"""Repository for auto-apply configuration."""

from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DBAutoApplyConfig
from src.utils.logger import get_logger


class AutoApplyConfigRepository:
    """Repository for managing auto-apply configurations."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository."""
        self.session = session
        self.logger = get_logger(__name__)

    async def create(self, config: DBAutoApplyConfig) -> DBAutoApplyConfig:
        """Create a new configuration.

        Args:
            config: The configuration to create

        Returns:
            The created configuration
        """
        try:
            async with self.session.begin():
                self.session.add(config)
                await self.session.flush()
                await self.session.refresh(config)
            return config
        except Exception as e:
            self.logger.error(f"Error creating auto-apply config: {e}")
            raise

    async def get_by_user_id(self, user_id: str) -> Optional[DBAutoApplyConfig]:
        """Get configuration by user ID.

        Args:
            user_id: The user ID

        Returns:
            The configuration or None if not found
        """
        try:
            stmt = select(DBAutoApplyConfig).where(DBAutoApplyConfig.user_id == user_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting auto-apply config: {e}")
            return None

    async def update(self, user_id: str, updates: dict) -> Optional[DBAutoApplyConfig]:
        """Update a configuration.

        Args:
            user_id: The user ID
            updates: Dictionary of fields to update

        Returns:
            The updated configuration or None if not found
        """
        try:
            async with self.session.begin():
                stmt = (
                    update(DBAutoApplyConfig)
                    .where(DBAutoApplyConfig.user_id == user_id)
                    .values(**updates)
                    .returning(DBAutoApplyConfig)
                )
                result = await self.session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error updating auto-apply config: {e}")
            raise

    async def get_active_configs(self) -> List[DBAutoApplyConfig]:
        """Get all active configurations.

        Returns:
            List of active configurations
        """
        try:
            stmt = select(DBAutoApplyConfig).where(DBAutoApplyConfig.enabled == True)
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            self.logger.error(f"Error getting active configs: {e}")
            return []
