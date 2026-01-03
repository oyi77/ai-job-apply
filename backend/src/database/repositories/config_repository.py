"""Repository for configuration management."""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from ..models import DBConfig
from loguru import logger


class ConfigRepository:
    """Repository for configuration data access."""
    
    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session."""
        self.session = session
        self.logger = logger.bind(module="ConfigRepository")
    
    async def create(self, name: str, key: str, value: str, description: Optional[str] = None) -> DBConfig:
        """Create a new configuration entry."""
        try:
            config = DBConfig(
                name=name,
                key=key,
                value=value,
                description=description
            )
            self.session.add(config)
            await self.session.commit()
            await self.session.refresh(config)
            self.logger.info(f"Created config: {name} ({key})")
            return config
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating config {key}: {e}", exc_info=True)
            raise
    
    async def get_by_id(self, config_id: str) -> Optional[DBConfig]:
        """Get a configuration by ID."""
        try:
            stmt = select(DBConfig).where(DBConfig.id == config_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting config by ID {config_id}: {e}", exc_info=True)
            return None
    
    async def get_by_key(self, key: str) -> Optional[DBConfig]:
        """Get a configuration by key."""
        try:
            stmt = select(DBConfig).where(DBConfig.key == key)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting config by key {key}: {e}", exc_info=True)
            return None
    
    async def get_by_name(self, name: str) -> Optional[DBConfig]:
        """Get a configuration by name."""
        try:
            stmt = select(DBConfig).where(DBConfig.name == name)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting config by name {name}: {e}", exc_info=True)
            return None
    
    async def get_all(self) -> List[DBConfig]:
        """Get all configurations."""
        try:
            stmt = select(DBConfig).order_by(DBConfig.name)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            self.logger.error(f"Error getting all configs: {e}", exc_info=True)
            return []
    
    async def get_all_dict(self) -> Dict[str, str]:
        """Get all configurations as a dictionary (key -> value)."""
        try:
            configs = await self.get_all()
            return {config.key: config.value for config in configs}
        except Exception as e:
            self.logger.error(f"Error getting configs as dict: {e}", exc_info=True)
            return {}
    
    async def update(self, config_id: str, updates: Dict[str, Any]) -> Optional[DBConfig]:
        """Update a configuration."""
        try:
            stmt = (
                update(DBConfig)
                .where(DBConfig.id == config_id)
                .values(**updates, updated_at=datetime.now(timezone.utc))
                .returning(DBConfig)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            config = result.scalar_one_or_none()
            if config:
                await self.session.refresh(config)
                self.logger.info(f"Updated config: {config.name} ({config.key})")
            return config
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating config {config_id}: {e}", exc_info=True)
            return None
    
    async def update_by_key(self, key: str, value: str, description: Optional[str] = None) -> Optional[DBConfig]:
        """Update a configuration by key."""
        try:
            config = await self.get_by_key(key)
            if not config:
                return None
            
            updates = {"value": value}
            if description is not None:
                updates["description"] = description
            
            return await self.update(config.id, updates)
        except Exception as e:
            self.logger.error(f"Error updating config by key {key}: {e}", exc_info=True)
            return None
    
    async def delete(self, config_id: str) -> bool:
        """Delete a configuration."""
        try:
            stmt = delete(DBConfig).where(DBConfig.id == config_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            deleted = result.rowcount > 0
            if deleted:
                self.logger.info(f"Deleted config: {config_id}")
            return deleted
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error deleting config {config_id}: {e}", exc_info=True)
            return False
    
    async def delete_by_key(self, key: str) -> bool:
        """Delete a configuration by key."""
        try:
            config = await self.get_by_key(key)
            if not config:
                return False
            return await self.delete(config.id)
        except Exception as e:
            self.logger.error(f"Error deleting config by key {key}: {e}", exc_info=True)
            return False
    
    async def upsert(self, name: str, key: str, value: str, description: Optional[str] = None) -> DBConfig:
        """Create or update a configuration."""
        try:
            existing = await self.get_by_key(key)
            if existing:
                updates = {"value": value, "name": name}
                if description is not None:
                    updates["description"] = description
                updated = await self.update(existing.id, updates)
                return updated if updated else existing
            else:
                return await self.create(name, key, value, description)
        except Exception as e:
            self.logger.error(f"Error upserting config {key}: {e}", exc_info=True)
            raise

