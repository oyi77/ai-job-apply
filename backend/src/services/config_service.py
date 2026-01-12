"""Configuration service for managing application settings."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from src.database.repositories.config_repository import ConfigRepository
from src.database.config import database_config
from loguru import logger


class ConfigService:
    """Service for managing application configuration."""
    
    def __init__(self):
        """Initialize the configuration service."""
        self.logger = logger.bind(module="ConfigService")
        self._cache: Optional[Dict[str, str]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = 60  # Cache for 60 seconds
    
    def _get_repository(self, session) -> ConfigRepository:
        """Get a repository instance with the given session."""
        return ConfigRepository(session)
    
    async def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value by key."""
        try:
            # Check cache first
            if self._cache is not None and self._cache_timestamp:
                age = (datetime.now(timezone.utc) - self._cache_timestamp).total_seconds()
                if age < self._cache_ttl and key in self._cache:
                    return self._cache[key]
            
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                config = await repo.get_by_key(key)
                if config:
                    # Update cache
                    if self._cache is None:
                        self._cache = {}
                    self._cache[key] = config.value
                    self._cache_timestamp = datetime.now(timezone.utc)
                    return config.value
                return default
        except Exception as e:
            self.logger.error(f"Error getting config {key}: {e}", exc_info=True)
            return default
    
    async def set(self, name: str, key: str, value: str, description: Optional[str] = None) -> bool:
        """Set a configuration value."""
        try:
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                await repo.upsert(name, key, value, description)
                # Invalidate cache
                self._cache = None
                self._cache_timestamp = None
                self.logger.info(f"Set config: {name} ({key})")
                return True
        except Exception as e:
            self.logger.error(f"Error setting config {key}: {e}", exc_info=True)
            return False
    
    async def get_all(self) -> Dict[str, str]:
        """Get all configurations as a dictionary."""
        try:
            # Check cache first
            if self._cache is not None and self._cache_timestamp:
                age = (datetime.now(timezone.utc) - self._cache_timestamp).total_seconds()
                if age < self._cache_ttl:
                    return self._cache.copy()
            
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                configs = await repo.get_all_dict()
                # Update cache
                self._cache = configs.copy()
                self._cache_timestamp = datetime.now(timezone.utc)
                return configs
        except Exception as e:
            self.logger.error(f"Error getting all configs: {e}", exc_info=True)
            return {}
    
    async def get_all_detailed(self) -> List[Dict[str, Any]]:
        """Get all configurations with full details."""
        try:
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                configs = await repo.get_all()
                return [
                    {
                        "id": config.id,
                        "name": config.name,
                        "key": config.key,
                        "value": config.value,
                        "description": config.description,
                        "created_at": config.created_at.isoformat() if config.created_at else None,
                        "updated_at": config.updated_at.isoformat() if config.updated_at else None,
                    }
                    for config in configs
                ]
        except Exception as e:
            self.logger.error(f"Error getting detailed configs: {e}", exc_info=True)
            return []
    
    async def delete(self, key: str) -> bool:
        """Delete a configuration."""
        try:
            async with database_config.get_session() as session:
                repo = self._get_repository(session)
                result = await repo.delete_by_key(key)
                # Invalidate cache
                self._cache = None
                self._cache_timestamp = None
                if result:
                    self.logger.info(f"Deleted config: {key}")
                return result
        except Exception as e:
            self.logger.error(f"Error deleting config {key}: {e}", exc_info=True)
            return False
    
    async def invalidate_cache(self):
        """Invalidate the configuration cache."""
        self._cache = None
        self._cache_timestamp = None
    
    async def get_ai_provider_configs(self) -> List[Dict[str, Any]]:
        """Get AI provider configurations from database."""
        try:
            configs = await self.get_all()
            providers = []
            
            # Define provider keys
            provider_keys = {
                "openai": ["openai_api_key", "openai_model", "openai_base_url"],
                "openrouter": ["openrouter_api_key", "openrouter_model", "openrouter_base_url"],
                "cursor": ["cursor_api_key", "cursor_model", "cursor_base_url"],
                "gemini": ["gemini_api_key", "gemini_model"],
                "local_ai": ["local_ai_base_url", "local_ai_model"],
            }
            
            for provider_name, keys in provider_keys.items():
                provider_config = {"provider_name": provider_name}
                for key in keys:
                    value = configs.get(key)
                    if value:
                        # Extract the setting name from key (e.g., "openai_api_key" -> "api_key")
                        setting_name = key.replace(f"{provider_name}_", "")
                        provider_config[setting_name] = value
                
                # Only add provider if it has at least an API key or base URL
                if "api_key" in provider_config or "base_url" in provider_config:
                    providers.append(provider_config)
            
            return providers
        except Exception as e:
            self.logger.error(f"Error getting AI provider configs: {e}", exc_info=True)
            return []

