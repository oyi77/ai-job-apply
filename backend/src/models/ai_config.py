"""Pydantic models for AI configuration."""

from typing import Optional, List
from pydantic import BaseModel, Field


class AIProviderConfigBase(BaseModel):
    """Base model for AI provider configuration."""

    is_enabled: bool = Field(
        default=False, description="Whether this provider is enabled"
    )
    priority: int = Field(
        default=0, description="Provider priority (lower = higher priority)"
    )
    api_base_url: Optional[str] = Field(default=None, description="API base URL")
    default_model: Optional[str] = Field(default=None, description="Default model name")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Temperature for generation"
    )
    max_tokens: int = Field(
        default=2048, ge=1, le=8192, description="Max tokens per response"
    )
    supports_resume_optimization: bool = Field(default=True)
    supports_cover_letter: bool = Field(default=True)
    supports_interview_prep: bool = Field(default=True)
    supports_career_insights: bool = Field(default=True)


class AIProviderConfigCreate(AIProviderConfigBase):
    """Model for creating a new AI provider configuration."""

    provider_name: str = Field(
        ..., min_length=1, max_length=50, description="Provider name"
    )
    api_key: Optional[str] = Field(
        default=None, description="API key (stored securely)"
    )


class AIProviderConfigUpdate(BaseModel):
    """Model for updating an AI provider configuration."""

    is_enabled: Optional[bool] = None
    priority: Optional[int] = None
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    default_model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=8192)
    supports_resume_optimization: Optional[bool] = None
    supports_cover_letter: Optional[bool] = None
    supports_interview_prep: Optional[bool] = None
    supports_career_insights: Optional[bool] = None


class AIProviderConfig(AIProviderConfigBase):
    """Model for AI provider configuration (response)."""

    id: str
    provider_name: str
    requests_today: int
    max_requests_daily: Optional[int]
    cost_today: float
    max_cost_daily: Optional[float]
    last_used_at: Optional[str]
    is_healthy: bool
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class GlobalAISettingsBase(BaseModel):
    """Base model for global AI settings."""

    active_provider: str = Field(default="gemini", description="Active AI provider")
    default_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    default_max_tokens: int = Field(default=2048, ge=1, le=8192)
    auto_retry_on_failure: bool = Field(default=True)
    max_retries: int = Field(default=3, ge=0, le=10)
    fallback_to_mock: bool = Field(default=True)
    rate_limit_requests_per_minute: int = Field(default=60, ge=1)
    rate_limit_tokens_per_minute: int = Field(default=100000, ge=1)
    log_prompts: bool = Field(default=False)
    log_responses: bool = Field(default=False)
    cache_enabled: bool = Field(default=True)
    cache_ttl_seconds: int = Field(default=3600, ge=0, le=86400)


class GlobalAISettingsUpdate(BaseModel):
    """Model for updating global AI settings."""

    active_provider: Optional[str] = None
    default_temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    default_max_tokens: Optional[int] = Field(default=None, ge=1, le=8192)
    auto_retry_on_failure: Optional[bool] = None
    max_retries: Optional[int] = Field(default=None, ge=0, le=10)
    fallback_to_mock: Optional[bool] = None
    rate_limit_requests_per_minute: Optional[int] = Field(default=None, ge=1)
    rate_limit_tokens_per_minute: Optional[int] = Field(default=None, ge=1)
    log_prompts: Optional[bool] = None
    log_responses: Optional[bool] = None
    cache_enabled: Optional[bool] = None
    cache_ttl_seconds: Optional[int] = Field(default=None, ge=0, le=86400)


class GlobalAISettings(GlobalAISettingsBase):
    """Model for global AI settings (response)."""

    id: str
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class AIProviderTestResult(BaseModel):
    """Model for AI provider test result."""

    status: str  # success, error, warning
    message: str
    provider: str
