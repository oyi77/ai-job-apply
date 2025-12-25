"""OpenRouter provider implementation."""

from typing import Optional
from openai import AsyncOpenAI
from .openai_provider import OpenAIProvider
from ...core.ai_provider import AIProviderConfig, AIResponse
from loguru import logger

class OpenRouterProvider(OpenAIProvider):
    """OpenRouter provider implementation extending OpenAIProvider."""
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.provider_name = "openrouter"
    
    async def initialize(self) -> bool:
        """Initialize OpenRouter client with specific headers."""
        try:
            if not self.config.api_key:
                logger.warning("OpenRouter API key not provided")
                return False
            
            # OpenRouter requires specific headers for best results
            # https://openrouter.ai/docs#headers
            extra_headers = {
                "HTTP-Referer": "https://github.com/oyi77/ai-job-apply", # Site URL
                "X-Title": "AI Job Apply Assistant", # Site Name
            }
            
            self.client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url or "https://openrouter.ai/api/v1",
                default_headers=extra_headers
            )
            
            # Test connection - listing models is a safe way to verify the API key
            await self.client.models.list()
            self._available = True
            logger.info("OpenRouter provider initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter provider: {e}")
            self._available = False
            return False

    async def generate_text(self, prompt: str, **kwargs) -> AIResponse:
        """Override generate_text to ensure provider name is set to openrouter."""
        response = await super().generate_text(prompt, **kwargs)
        response.provider = "openrouter"
        return response
