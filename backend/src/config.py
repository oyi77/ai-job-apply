"""Configuration management for the AI Job Application Assistant."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from .core.ai_provider import AIProviderConfig

class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "AI Job Application Assistant"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Database
    database_url: str = Field(default="sqlite:///./job_applications.db", env="DATABASE_URL")
    
    # AI Providers Configuration
    ai_providers: List[AIProviderConfig] = Field(default_factory=list)
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_base_url: Optional[str] = Field(default=None, env="OPENAI_BASE_URL")
    
    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="meta-llama/llama-3-8b-instruct", env="OPENROUTER_MODEL")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")
    
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
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173"], env="CORS_ORIGINS")
    
    # JWT Configuration
    jwt_secret_key: str = Field(default="your-secret-key-here", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=15, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", env="LOG_FILE")
    
    # Legacy fields for backward compatibility
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173"], env="CORS_ORIGINS")
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
    
    def _setup_ai_providers(self):
        """Setup AI providers configuration."""
        providers = []
        
        # OpenAI Provider
        if self.openai_api_key:
            providers.append(AIProviderConfig(
                provider_name="openai",
                api_key=self.openai_api_key,
                base_url=self.openai_base_url,
                model=self.openai_model,
                temperature=0.7,
                max_tokens=1000,
                timeout=30
            ))
        
        # Local AI Provider
        if self.local_ai_base_url:
            providers.append(AIProviderConfig(
                provider_name="local_ai",
                base_url=self.local_ai_base_url,
                model=self.local_ai_model,
                temperature=0.7,
                max_tokens=1000,
                timeout=30
            ))
        
        # Gemini Provider (legacy, for backward compatibility)
        if self.gemini_api_key:
            providers.append(AIProviderConfig(
                provider_name="gemini",
                api_key=self.gemini_api_key,
                model=self.gemini_model,
                temperature=0.7,
                max_tokens=1000,
                timeout=30
            ))
        
        # OpenRouter Provider
        if self.openrouter_api_key:
            providers.append(AIProviderConfig(
                provider_name="openrouter",
                api_key=self.openrouter_api_key,
                base_url=self.openrouter_base_url,
                model=self.openrouter_model,
                temperature=0.7,
                max_tokens=1000,
                timeout=30
            ))
        
        self.ai_providers = providers

# Global config instance
config = Settings() 