"""Configuration management for the AI Job Application Assistant."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the AI Job Application Assistant."""
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # AI Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Job Search Configuration
    HEADLESS_BROWSER = os.getenv("HEADLESS_BROWSER", "true").lower() == "true"
    REQUEST_DELAY = int(os.getenv("REQUEST_DELAY", "2"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30"))
    MAX_RESULTS_PER_SITE = int(os.getenv("MAX_RESULTS_PER_SITE", "50"))
    
    # File Configuration
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    RESUME_DIR = os.getenv("RESUME_DIR", "./resumes")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
    TEMPLATES_DIR = os.getenv("TEMPLATES_DIR", "./templates")
    MAX_FILE_SIZE_MB = float(os.getenv("MAX_FILE_SIZE_MB", "10.0"))
    ALLOWED_FILE_TYPES = [".pdf", ".docx", ".txt"]
    
    # Security Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    CORS_ORIGINS = ["*"]  # Simplified for now
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_DIR = os.getenv("LOG_DIR", "./logs")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Job search defaults
    DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "Remote")
    DEFAULT_KEYWORDS = ["python", "developer", "software engineer"]
    DEFAULT_EXPERIENCE_LEVEL = os.getenv("DEFAULT_EXPERIENCE_LEVEL", "entry")
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration and create directories."""
        # Validate required settings
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        
        # Validate environment
        allowed_envs = ["development", "staging", "production", "testing"]
        if cls.ENVIRONMENT not in allowed_envs:
            raise ValueError(f"Environment must be one of: {allowed_envs}")
        
        # Validate log level
        allowed_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL not in allowed_log_levels:
            raise ValueError(f"Log level must be one of: {allowed_log_levels}")
        
        # Create directories
        cls.create_directories()
    
    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories."""
        directories = [
            cls.UPLOAD_DIR,
            cls.RESUME_DIR,
            cls.OUTPUT_DIR,
            cls.TEMPLATES_DIR,
            cls.LOG_DIR,
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.ENVIRONMENT == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment."""
        return cls.ENVIRONMENT == "development"


# Global configuration instance
config = Config()

# Backward compatibility
GEMINI_API_KEY = config.GEMINI_API_KEY
HEADLESS_BROWSER = config.HEADLESS_BROWSER
REQUEST_DELAY = config.REQUEST_DELAY
MAX_RETRIES = config.MAX_RETRIES
DEFAULT_LOCATION = config.DEFAULT_LOCATION
DEFAULT_KEYWORDS = config.DEFAULT_KEYWORDS
DEFAULT_EXPERIENCE_LEVEL = config.DEFAULT_EXPERIENCE_LEVEL 