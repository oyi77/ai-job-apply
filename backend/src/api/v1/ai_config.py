"""AI Configuration API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from src.database.config import get_db_session
from src.database.models import (
    AIProviderConfig as AIProviderConfigDB,
    GlobalAISettings as GlobalAISettingsDB,
)
from src.models.ai_config import (
    AIProviderConfig as AIProviderConfigModel,
    AIProviderConfigUpdate,
    AIProviderConfigCreate,
    GlobalAISettings as GlobalAISettingsModel,
    GlobalAISettingsUpdate,
    AIProviderTestResult,
)

router = APIRouter(prefix="/ai-config", tags=["AI Configuration"])


@router.get("/providers", response_model=List[AIProviderConfigModel])
async def get_providers(session: AsyncSession = Depends(get_db_session)):
    """Get all AI provider configurations."""
    result = await session.execute(
        select(AIProviderConfigDB).order_by(AIProviderConfigDB.priority)
    )
    providers = result.scalars().all()
    return [p.to_dict() for p in providers]


@router.get("/providers/{provider_name}", response_model=AIProviderConfigModel)
async def get_provider(
    provider_name: str, session: AsyncSession = Depends(get_db_session)
):
    """Get a specific AI provider configuration."""
    result = await session.execute(
        select(AIProviderConfigDB).where(
            AIProviderConfigDB.provider_name == provider_name
        )
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=404, detail=f"Provider '{provider_name}' not found"
        )
    return provider.to_dict()


@router.post(
    "/providers",
    response_model=AIProviderConfigModel,
    status_code=status.HTTP_201_CREATED,
)
async def create_provider(
    config: AIProviderConfigCreate, session: AsyncSession = Depends(get_db_session)
):
    """Create a new AI provider configuration."""
    # Check if provider already exists
    result = await session.execute(
        select(AIProviderConfigDB).where(
            AIProviderConfigDB.provider_name == config.provider_name
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=400, detail=f"Provider '{config.provider_name}' already exists"
        )

    provider = AIProviderConfigDB(
        provider_name=config.provider_name,
        is_enabled=config.is_enabled,
        priority=config.priority,
        api_key_encrypted=config.api_key,
        api_base_url=config.api_base_url,
        default_model=config.default_model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        supports_resume_optimization=config.supports_resume_optimization,
        supports_cover_letter=config.supports_cover_letter,
        supports_interview_prep=config.supports_interview_prep,
        supports_career_insights=config.supports_career_insights,
    )
    session.add(provider)
    await session.commit()
    await session.refresh(provider)
    return provider.to_dict()


@router.put("/providers/{provider_name}", response_model=AIProviderConfigModel)
async def update_provider(
    provider_name: str,
    updates: AIProviderConfigUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update an AI provider configuration."""
    result = await session.execute(
        select(AIProviderConfigDB).where(
            AIProviderConfigDB.provider_name == provider_name
        )
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=404, detail=f"Provider '{provider_name}' not found"
        )

    # Update fields
    if updates.is_enabled is not None:
        provider.is_enabled = updates.is_enabled
    if updates.priority is not None:
        provider.priority = updates.priority
    if updates.api_key is not None:
        provider.api_key_encrypted = updates.api_key
    if updates.api_base_url is not None:
        provider.api_base_url = updates.api_base_url
    if updates.default_model is not None:
        provider.default_model = updates.default_model
    if updates.temperature is not None:
        provider.temperature = updates.temperature
    if updates.max_tokens is not None:
        provider.max_tokens = updates.max_tokens
    if updates.supports_resume_optimization is not None:
        provider.supports_resume_optimization = updates.supports_resume_optimization
    if updates.supports_cover_letter is not None:
        provider.supports_cover_letter = updates.supports_cover_letter
    if updates.supports_interview_prep is not None:
        provider.supports_interview_prep = updates.supports_interview_prep
    if updates.supports_career_insights is not None:
        provider.supports_career_insights = updates.supports_career_insights

    provider.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(provider)
    return provider.to_dict()


@router.delete("/providers/{provider_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_name: str, session: AsyncSession = Depends(get_db_session)
):
    """Delete an AI provider configuration."""
    result = await session.execute(
        select(AIProviderConfigDB).where(
            AIProviderConfigDB.provider_name == provider_name
        )
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=404, detail=f"Provider '{provider_name}' not found"
        )

    await session.delete(provider)
    await session.commit()


@router.post("/providers/{provider_name}/test", response_model=AIProviderTestResult)
async def test_provider(
    provider_name: str, session: AsyncSession = Depends(get_db_session)
):
    """Test an AI provider configuration by making a simple API call."""
    result = await session.execute(
        select(AIProviderConfigDB).where(
            AIProviderConfigDB.provider_name == provider_name
        )
    )
    provider = result.scalar_one_or_none()
    if not provider:
        raise HTTPException(
            status_code=404, detail=f"Provider '{provider_name}' not found"
        )

    if not provider.api_key_encrypted:
        return AIProviderTestResult(
            status="error",
            message="API key not configured",
            provider=provider_name,
        )

    # Test the provider
    try:
        if provider_name in ["gemini", "google"]:
            from src.services.gemini_ai_service import GeminiAIService

            temp_service = GeminiAIService(api_key=provider.api_key_encrypted)
            is_available = await temp_service.is_available()
            return AIProviderTestResult(
                status="success" if is_available else "warning",
                message="Gemini API connection successful"
                if is_available
                else "API key may be invalid",
                provider=provider_name,
            )
        elif provider_name == "openai":
            return AIProviderTestResult(
                status="info",
                message="OpenAI test not yet implemented",
                provider=provider_name,
            )
        else:
            return AIProviderTestResult(
                status="info",
                message=f"Test not implemented for {provider_name}",
                provider=provider_name,
            )
    except Exception as e:
        provider.last_error = str(e)
        provider.is_healthy = False
        await session.commit()
        return AIProviderTestResult(
            status="error",
            message=str(e),
            provider=provider_name,
        )


# Global Settings Endpoints


@router.get("/settings", response_model=GlobalAISettingsModel)
async def get_global_settings(session: AsyncSession = Depends(get_db_session)):
    """Get global AI settings."""
    result = await session.execute(select(GlobalAISettingsDB))
    settings = result.scalar_one_or_none()

    if not settings:
        # Create default settings
        settings = GlobalAISettingsDB()
        session.add(settings)
        await session.commit()
        await session.refresh(settings)

    return settings.to_dict()


@router.put("/settings", response_model=GlobalAISettingsModel)
async def update_global_settings(
    updates: GlobalAISettingsUpdate, session: AsyncSession = Depends(get_db_session)
):
    """Update global AI settings."""
    result = await session.execute(select(GlobalAISettingsDB))
    settings = result.scalar_one_or_none()

    if not settings:
        settings = GlobalAISettingsDB()
        session.add(settings)
        await session.commit()
        await session.refresh(settings)

    # Update fields
    if updates.active_provider is not None:
        settings.active_provider = updates.active_provider
    if updates.default_temperature is not None:
        settings.default_temperature = updates.default_temperature
    if updates.default_max_tokens is not None:
        settings.default_max_tokens = updates.default_max_tokens
    if updates.auto_retry_on_failure is not None:
        settings.auto_retry_on_failure = updates.auto_retry_on_failure
    if updates.max_retries is not None:
        settings.max_retries = updates.max_retries
    if updates.fallback_to_mock is not None:
        settings.fallback_to_mock = updates.fallback_to_mock
    if updates.rate_limit_requests_per_minute is not None:
        settings.rate_limit_requests_per_minute = updates.rate_limit_requests_per_minute
    if updates.rate_limit_tokens_per_minute is not None:
        settings.rate_limit_tokens_per_minute = updates.rate_limit_tokens_per_minute
    if updates.log_prompts is not None:
        settings.log_prompts = updates.log_prompts
    if updates.log_responses is not None:
        settings.log_responses = updates.log_responses
    if updates.cache_enabled is not None:
        settings.cache_enabled = updates.cache_enabled
    if updates.cache_ttl_seconds is not None:
        settings.cache_ttl_seconds = updates.cache_ttl_seconds

    settings.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(settings)
    return settings.to_dict()


@router.post("/settings/reset", response_model=GlobalAISettingsModel)
async def reset_global_settings(session: AsyncSession = Depends(get_db_session)):
    """Reset global AI settings to defaults."""
    result = await session.execute(select(GlobalAISettingsDB))
    settings = result.scalar_one_or_none()

    if settings:
        await session.delete(settings)

    settings = GlobalAISettingsDB()
    session.add(settings)
    await session.commit()
    await session.refresh(settings)
    return settings.to_dict()


@router.get("/health", response_model=dict)
async def ai_health_check(session: AsyncSession = Depends(get_db_session)):
    """Check AI service health across all providers."""
    result = await session.execute(
        select(AIProviderConfigDB).where(AIProviderConfigDB.is_enabled == True)
    )
    providers = result.scalars().all()

    health_status = []
    for provider in providers:
        health_status.append(
            {
                "provider": provider.provider_name,
                "healthy": provider.is_healthy,
                "last_used": provider.last_used_at.isoformat()
                if provider.last_used_at
                else None,
                "requests_today": provider.requests_today,
            }
        )

    # Get active provider
    result = await session.execute(select(GlobalAISettingsDB))
    settings = result.scalar_one_or_none()

    return {
        "active_provider": settings.active_provider if settings else "gemini",
        "providers": health_status,
        "total_enabled": len(providers),
    }
