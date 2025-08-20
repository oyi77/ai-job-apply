"""Abstract base class for AI providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class AIProviderConfig(BaseModel):
    """Configuration for AI providers."""
    provider_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 30

class AIResponse(BaseModel):
    """Standardized AI response format."""
    content: str
    provider: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: AIProviderConfig):
        self.config = config
        self.provider_name = config.provider_name
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the AI provider."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available."""
        pass
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> AIResponse:
        """Generate text using the AI provider."""
        pass
    
    @abstractmethod
    async def optimize_resume(self, resume_content: str, job_description: str) -> AIResponse:
        """Optimize resume for a specific job."""
        pass
    
    @abstractmethod
    async def generate_cover_letter(self, resume_content: str, job_description: str, company: str) -> AIResponse:
        """Generate a cover letter."""
        pass
    
    @abstractmethod
    async def analyze_job_match(self, resume_content: str, job_description: str) -> AIResponse:
        """Analyze job-resume match."""
        pass
    
    @abstractmethod
    async def extract_skills(self, text: str) -> AIResponse:
        """Extract skills from text."""
        pass
