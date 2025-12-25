"""Unit tests for AI providers."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.core.ai_provider import AIProviderConfig
from src.services.providers.openai_provider import OpenAIProvider
from src.services.providers.openrouter_provider import OpenRouterProvider

@pytest.fixture
def openai_config():
    return AIProviderConfig(
        provider_name="openai",
        api_key="sk-test-key",
        model="gpt-4",
        temperature=0.7,
        max_tokens=1000
    )

@pytest.fixture
def openrouter_config():
    return AIProviderConfig(
        provider_name="openrouter",
        api_key="sk-or-test-key",
        model="meta-llama/llama-3-8b-instruct",
        base_url="https://openrouter.ai/api/v1"
    )

@pytest.mark.asyncio
async def test_openai_provider_initialization(openai_config):
    """Test OpenAI provider initialization."""
    with patch("src.services.providers.openai_provider.AsyncOpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.models.list = AsyncMock()
        mock_openai.return_value = mock_client
        
        provider = OpenAIProvider(openai_config)
        success = await provider.initialize()
        
        assert success is True
        assert await provider.is_available() is True
        mock_openai.assert_called_once_with(
            api_key=openai_config.api_key,
            base_url=openai_config.base_url
        )

@pytest.mark.asyncio
async def test_openrouter_provider_initialization(openrouter_config):
    """Test OpenRouter provider initialization."""
    with patch("src.services.providers.openrouter_provider.AsyncOpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_client.models.list = AsyncMock()
        mock_openai.return_value = mock_client
        
        provider = OpenRouterProvider(openrouter_config)
        success = await provider.initialize()
        
        assert success is True
        assert await provider.is_available() is True
        # Verify OpenRouter specific headers
        kwargs = mock_openai.call_args.kwargs
        assert "default_headers" in kwargs
        assert kwargs["default_headers"]["X-Title"] == "AI Job Apply Assistant"
        assert kwargs["api_key"] == openrouter_config.api_key
        assert kwargs["base_url"] == openrouter_config.base_url

@pytest.mark.asyncio
async def test_openai_provider_generate_text(openai_config):
    """Test OpenAI provider text generation."""
    with patch("src.services.providers.openai_provider.AsyncOpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Optimized resume content"
        mock_choice.finish_reason = "stop"
        mock_completion.choices = [mock_choice]
        mock_completion.usage.prompt_tokens = 10
        mock_completion.usage.completion_tokens = 20
        mock_completion.usage.total_tokens = 30
        mock_completion.id = "test-id"
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_client.models.list = AsyncMock()
        mock_openai.return_value = mock_client
        
        provider = OpenAIProvider(openai_config)
        await provider.initialize()
        
        response = await provider.generate_text("Please optimize this resume")
        
        assert response.content == "Optimized resume content"
        assert response.provider == "openai"
        assert response.model == openai_config.model
        assert response.usage["total_tokens"] == 30

@pytest.mark.asyncio
async def test_openrouter_provider_generate_text(openrouter_config):
    """Test OpenRouter provider text generation."""
    with patch("src.services.providers.openrouter_provider.AsyncOpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "OpenRouter optimized content"
        mock_choice.finish_reason = "stop"
        mock_completion.choices = [mock_choice]
        mock_completion.usage.prompt_tokens = 15
        mock_completion.usage.completion_tokens = 25
        mock_completion.usage.total_tokens = 40
        mock_completion.id = "or-test-id"
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_client.models.list = AsyncMock()
        mock_openai.return_value = mock_client
        
        provider = OpenRouterProvider(openrouter_config)
        await provider.initialize()
        
        response = await provider.generate_text("Optimize this resume via OpenRouter")
        
        assert response.content == "OpenRouter optimized content"
        assert response.provider == "openrouter" # Check that override works
        assert response.model == openrouter_config.model
