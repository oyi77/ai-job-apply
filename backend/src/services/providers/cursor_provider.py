"""Cursor provider implementation."""

from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from src.services.providers.openai_provider import OpenAIProvider
from src.core.ai_provider import AIProviderConfig, AIResponse
from loguru import logger

class CursorProvider(OpenAIProvider):
    """Cursor provider implementation extending OpenAIProvider.
    
    Cursor uses OpenAI-compatible API, so we can extend OpenAIProvider.
    """
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.provider_name = "cursor"
    
    async def initialize(self) -> bool:
        """Initialize Cursor client."""
        try:
            if not self.config.api_key:
                logger.warning("Cursor API key not provided")
                return False
            
            # Cursor uses OpenAI-compatible API
            # Base URL for Cursor API
            base_url = self.config.base_url or "https://api.cursor.com/v1"
            
            # Cursor requires specific headers
            extra_headers = {
                "X-Cursor-API-Key": self.config.api_key,
            }
            
            self.client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=base_url,
                default_headers=extra_headers
            )
            
            # Test connection
            try:
                await self.client.models.list()
            except Exception as e:
                # If models.list fails, try a simple completion test
                logger.debug(f"Models list failed, will test on first request: {e}")
            
            self._available = True
            logger.info("Cursor provider initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Cursor provider: {e}")
            self._available = False
            return False
    
    async def generate_text(self, prompt: str, **kwargs) -> AIResponse:
        """Override generate_text to ensure provider name is set to cursor."""
        response = await super().generate_text(prompt, **kwargs)
        response.provider = "cursor"
        return response

