"""Gemini API Client wrapper."""

import os
from typing import Optional, List, Dict, Any
from google import genai
from google.genai import types
from loguru import logger
from src.config import config


class GeminiClient:
    """Wrapper for Google Gemini API client."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client.

        Args:
            api_key: Optional API key. If not provided, tries to load from config/env.
        """
        self.logger = logger.bind(module="GeminiClient")
        self.api_key = api_key or config.GEMINI_API_KEY
        self.client: Optional[genai.Client] = None
        self.model_name = "gemini-1.5-flash"
        self.temperature = 0.7
        self.max_tokens = 2048

        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the underlying genai Client."""
        try:
            if self.api_key:
                self.client = genai.Client(api_key=self.api_key)
                self.logger.info(
                    f"Gemini Client initialized with model: {self.model_name}"
                )
            else:
                self.logger.warning("Gemini API key not configured, client disabled")
                self.client = None
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini Client: {e}")
            self.client = None

    def is_available(self) -> bool:
        """Check if client is initialized and available."""
        return self.client is not None and bool(self.api_key)

    def configure(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> None:
        """Update client configuration."""
        if model_name:
            self.model_name = model_name
        if temperature is not None:
            self.temperature = temperature
        if max_tokens is not None:
            self.max_tokens = max_tokens

    async def generate_content(self, prompt: str) -> Optional[str]:
        """Generate content using Gemini model.

        Args:
            prompt: Input prompt text

        Returns:
            Generated text response or None if failed
        """
        try:
            if not self.client:
                return None

            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                ),
            )

            return response.text if response and response.text else None

        except Exception as e:
            self.logger.error(f"Error generating content: {e}", exc_info=True)
            return None
