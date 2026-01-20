"""Configuration management for the AI Job Application Assistant."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from src.core.ai_provider import AIProviderConfig


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "AI Job Application Assistant"
    app_version: str = "1.0.0"
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    debug: bool = Field(default=False, env="DEBUG")

    # Server
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # Database
    database_url: str = Field(
        default="sqlite:///./job_applications.db", env="DATABASE_URL"
    )

    # AI Providers Configuration
    ai_providers: List[AIProviderConfig] = Field(default_factory=list)

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_base_url: Optional[str] = Field(default=None, env="OPENAI_BASE_URL")

    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    openrouter_model: str = Field(
        default="meta-llama/llama-3-8b-instruct", env="OPENROUTER_MODEL"
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL"
    )

    # Cursor Configuration
    cursor_api_key: Optional[str] = Field(default=None, env="CURSOR_API_KEY")
    cursor_model: str = Field(default="gpt-4", env="CURSOR_MODEL")
    cursor_base_url: str = Field(
        default="https://api.cursor.com/v1", env="CURSOR_BASE_URL"
    )

    # Local AI Configuration
    local_ai_base_url: Optional[str] = Field(default=None, env="LOCAL_AI_BASE_URL")
    local_ai_model: str = Field(default="llama2", env="LOCAL_AI_MODEL")

    # Gemini Configuration (legacy)
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", env="GEMINI_MODEL")

    # File Storage
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB

    # Security
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"], env="CORS_ORIGINS"
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_auth_per_minute: int = Field(
        default=10, env="RATE_LIMIT_AUTH_PER_MINUTE"
    )
    rate_limit_api_per_minute: int = Field(default=60, env="RATE_LIMIT_API_PER_MINUTE")

    # Account Lockout
    account_lockout_enabled: bool = Field(default=True, env="ACCOUNT_LOCKOUT_ENABLED")
    max_failed_login_attempts: int = Field(default=5, env="MAX_FAILED_LOGIN_ATTEMPTS")
    account_lockout_duration_minutes: int = Field(
        default=30, env="ACCOUNT_LOCKOUT_DURATION_MINUTES"
    )

    # JWT Configuration
    jwt_secret_key: str = Field(default="your-secret-key-here", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=15, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # Email settings
    smtp_host: str = Field(default="localhost", env="SMTP_HOST")
    smtp_port: int = Field(default=1025, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_tls: bool = Field(default=False, env="SMTP_TLS")
    emails_from_email: str = Field(
        default="noreply@example.com", env="EMAILS_FROM_EMAIL"
    )
    emails_from_name: Optional[str] = Field(
        default="AI Job Application Assistant", env="EMAILS_FROM_NAME"
    )

    # Mailgun settings
    mailgun_api_key: Optional[str] = Field(default=None, env="MAILGUN_API_KEY")
    mailgun_domain: Optional[str] = Field(default=None, env="MAILGUN_DOMAIN")
    mailgun_region: str = Field(default="us", env="MAILGUN_REGION")
    mailgun_from_email: str = Field(
        default="noreply@example.com", env="MAILGUN_FROM_EMAIL"
    )
    mailgun_from_name: str = Field(
        default="AI Job Application Assistant", env="MAILGUN_FROM_NAME"
    )

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", env="LOG_FILE")

    # Caching
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    cache_backend: str = Field(default="dogpile.cache.redis", env="CACHE_BACKEND")
    cache_expiration_time: int = Field(
        default=3600, env="CACHE_EXPIRATION_TIME"
    )  # 1 hour

    # Legacy fields for backward compatibility
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"], env="CORS_ORIGINS"
    )
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    RESUME_DIR: str = Field(default="./resumes", env="RESUME_DIR")
    OUTPUT_DIR: str = Field(default="./output", env="OUTPUT_DIR")
    TEMPLATES_DIR: str = Field(default="./templates", env="TEMPLATES_DIR")
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from environment

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_ai_providers()

    async def load_from_database(self):
        """Load AI provider configurations from database."""
        try:
            from src.services.config_service import ConfigService

            config_service = ConfigService()
            db_configs = await config_service.get_all()

            # Override with database values if they exist
            self.openai_api_key = (
                db_configs.get("openai_api_key") or self.openai_api_key
            )
            self.openai_model = db_configs.get("openai_model") or self.openai_model
            self.openai_base_url = (
                db_configs.get("openai_base_url") or self.openai_base_url
            )

            self.openrouter_api_key = (
                db_configs.get("openrouter_api_key") or self.openrouter_api_key
            )
            self.openrouter_model = (
                db_configs.get("openrouter_model") or self.openrouter_model
            )
            self.openrouter_base_url = (
                db_configs.get("openrouter_base_url") or self.openrouter_base_url
            )

            self.cursor_api_key = (
                db_configs.get("cursor_api_key") or self.cursor_api_key
            )
            self.cursor_model = db_configs.get("cursor_model") or self.cursor_model
            self.cursor_base_url = (
                db_configs.get("cursor_base_url") or self.cursor_base_url
            )

            self.gemini_api_key = (
                db_configs.get("gemini_api_key") or self.gemini_api_key
            )
            self.gemini_model = db_configs.get("gemini_model") or self.gemini_model

            self.local_ai_base_url = (
                db_configs.get("local_ai_base_url") or self.local_ai_base_url
            )
            self.local_ai_model = (
                db_configs.get("local_ai_model") or self.local_ai_model
            )

            # Rebuild providers with updated values
            self._setup_ai_providers()
        except Exception as e:
            # If database is not available, use environment variables
            import logging

            logging.warning(
                f"Could not load configs from database: {e}. Using environment variables."
            )

    def _setup_ai_providers(self):
        """Setup AI providers configuration."""
        providers = []

        # OpenAI Provider
        if self.openai_api_key:
            providers.append(
                AIProviderConfig(
                    provider_name="openai",
                    api_key=self.openai_api_key,
                    base_url=self.openai_base_url,
                    model=self.openai_model,
                    temperature=0.7,
                    max_tokens=1000,
                    timeout=30,
                )
            )

        # Local AI Provider
        if self.local_ai_base_url:
            providers.append(
                AIProviderConfig(
                    provider_name="local_ai",
                    base_url=self.local_ai_base_url,
                    model=self.local_ai_model,
                    temperature=0.7,
                    max_tokens=1000,
                    timeout=30,
                )
            )

        # Gemini Provider (legacy, for backward compatibility)
        if self.gemini_api_key:
            providers.append(
                AIProviderConfig(
                    provider_name="gemini",
                    api_key=self.gemini_api_key,
                    model=self.gemini_model,
                    temperature=0.7,
                    max_tokens=1000,
                    timeout=30,
                )
            )

        # OpenRouter Provider
        if self.openrouter_api_key:
            providers.append(
                AIProviderConfig(
                    provider_name="openrouter",
                    api_key=self.openrouter_api_key,
                    base_url=self.openrouter_base_url,
                    model=self.openrouter_model,
                    temperature=0.7,
                    max_tokens=1000,
                    timeout=30,
                )
            )

        # Cursor Provider
        if self.cursor_api_key:
            providers.append(
                AIProviderConfig(
                    provider_name="cursor",
                    api_key=self.cursor_api_key,
                    base_url=self.cursor_base_url,
                    model=self.cursor_model,
                    temperature=0.7,
                    max_tokens=2000,
                    timeout=60,
                )
            )

        self.ai_providers = providers


# Global config instance
config = Settings()
