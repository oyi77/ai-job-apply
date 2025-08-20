"""AI Provider Manager for handling multiple AI providers."""

from typing import Dict, List, Optional, Type
from ...core.ai_provider import AIProvider, AIProviderConfig, AIResponse
from .providers.openai_provider import OpenAIProvider
from .providers.local_ai_provider import LocalAIProvider
from loguru import logger

class AIProviderManager:
    """Manages multiple AI providers with fallback support."""
    
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self.provider_order: List[str] = []
        self._initialized = False
    
    async def initialize(self, configs: List[AIProviderConfig]) -> bool:
        """Initialize all AI providers."""
        try:
            for config in configs:
                provider = await self._create_provider(config)
                if provider:
                    self.providers[config.provider_name] = provider
                    self.provider_order.append(config.provider_name)
                    logger.info(f"AI provider '{config.provider_name}' registered")
            
            self._initialized = True
            logger.info(f"AI Provider Manager initialized with {len(self.providers)} providers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Provider Manager: {e}")
            return False
    
    async def _create_provider(self, config: AIProviderConfig) -> Optional[AIProvider]:
        """Create and initialize a provider based on configuration."""
        try:
            if config.provider_name == "openai":
                provider = OpenAIProvider(config)
            elif config.provider_name == "local_ai":
                provider = LocalAIProvider(config)
            else:
                logger.warning(f"Unknown provider type: {config.provider_name}")
                return None
            
            if await provider.initialize():
                return provider
            else:
                logger.warning(f"Provider '{config.provider_name}' failed to initialize")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create provider '{config.provider_name}': {e}")
            return None
    
    async def get_available_provider(self) -> Optional[AIProvider]:
        """Get the first available provider."""
        for provider_name in self.provider_order:
            provider = self.providers.get(provider_name)
            if provider and await provider.is_available():
                return provider
        return None
    
    async def get_provider(self, provider_name: str) -> Optional[AIProvider]:
        """Get a specific provider by name."""
        provider = self.providers.get(provider_name)
        if provider and await provider.is_available():
            return provider
        return None
    
    async def is_any_available(self) -> bool:
        """Check if any provider is available."""
        return await self.get_available_provider() is not None
    
    async def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers."""
        status = {}
        for name, provider in self.providers.items():
            status[name] = await provider.is_available()
        return status
    
    async def generate_text(self, prompt: str, preferred_provider: Optional[str] = None, **kwargs) -> AIResponse:
        """Generate text using available provider."""
        provider = None
        
        # Try preferred provider first
        if preferred_provider:
            provider = await self.get_provider(preferred_provider)
        
        # Fall back to first available provider
        if not provider:
            provider = await self.get_available_provider()
        
        if not provider:
            raise RuntimeError("No AI providers available")
        
        return await provider.generate_text(prompt, **kwargs)
    
    async def optimize_resume(self, resume_content: str, job_description: str, preferred_provider: Optional[str] = None) -> AIResponse:
        """Optimize resume using available provider."""
        provider = None
        
        if preferred_provider:
            provider = await self.get_provider(preferred_provider)
        
        if not provider:
            provider = await self.get_available_provider()
        
        if not provider:
            raise RuntimeError("No AI providers available")
        
        return await provider.optimize_resume(resume_content, job_description)
    
    async def generate_cover_letter(self, resume_content: str, job_description: str, company: str, preferred_provider: Optional[str] = None) -> AIResponse:
        """Generate cover letter using available provider."""
        provider = None
        
        if preferred_provider:
            provider = await self.get_provider(preferred_provider)
        
        if not provider:
            provider = await self.get_available_provider()
        
        if not provider:
            raise RuntimeError("No AI providers available")
        
        return await provider.generate_cover_letter(resume_content, job_description, company)
    
    async def analyze_job_match(self, resume_content: str, job_description: str, preferred_provider: Optional[str] = None) -> AIResponse:
        """Analyze job match using available provider."""
        provider = None
        
        if preferred_provider:
            provider = await self.get_provider(preferred_provider)
        
        if not provider:
            provider = await self.get_available_provider()
        
        if not provider:
            raise RuntimeError("No AI providers available")
        
        return await provider.analyze_job_match(resume_content, job_description)
    
    async def extract_skills(self, text: str, preferred_provider: Optional[str] = None) -> AIResponse:
        """Extract skills using available provider."""
        provider = None
        
        if preferred_provider:
            provider = await self.get_provider(preferred_provider)
        
        if not provider:
            provider = await self.get_available_provider()
        
        if not provider:
            raise RuntimeError("No AI providers available")
        
        return await provider.extract_skills(text)
