"""Unified service registry for dependency injection in the AI Job Application Assistant."""

from typing import Dict, Any
from loguru import logger
from abc import ABC, abstractmethod

from ..core.ai_service import AIService
from ..core.file_service import FileService
from ..core.resume_service import ResumeService
from ..core.application_service import ApplicationService
from ..core.job_search import JobSearchService
from ..core.cover_letter_service import CoverLetterService
from ..core.job_application import JobApplicationService


class ServiceProvider(ABC):
    """Abstract base class for service providers."""
    
    @abstractmethod
    def get_service(self) -> Any:
        """Get the service instance."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up the service."""
        pass


class ServiceRegistry:
    """Unified service registry with dependency injection and lifecycle management."""
    
    def __init__(self):
        """Initialize the service registry."""
        self._services: Dict[str, ServiceProvider] = {}
        self._instances: Dict[str, Any] = {}
        self._initialized = False
        self._logger = logger.bind(module="ServiceRegistry")
    
    def register_service(self, name: str, provider: ServiceProvider) -> None:
        """Register a service provider."""
        self._services[name] = provider
        self._logger.info(f"Registered service provider: {name}")
    
    async def initialize(self) -> None:
        """Initialize all services in dependency order."""
        if self._initialized:
            return
        
        try:
            self._logger.info("Initializing service registry...")
            
            # Initialize services in dependency order
            await self._initialize_core_services()
            await self._initialize_business_services()
            
            self._initialized = True
            self._logger.info("Service registry initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing service registry: {e}", exc_info=True)
            raise
    
    async def _initialize_core_services(self) -> None:
        """Initialize core infrastructure services."""
        # File service (no dependencies)
        from .local_file_service import LocalFileService
        file_provider = LocalFileServiceProvider()
        self.register_service('file_service', file_provider)
        await file_provider.initialize()
        self._instances['file_service'] = file_provider.get_service()
        
        # AI service (no dependencies)
        from .gemini_ai_service import GeminiAIService
        ai_provider = GeminiAIProvider()
        self.register_service('ai_service', ai_provider)
        await ai_provider.initialize()
        self._instances['ai_service'] = ai_provider.get_service()
    
    async def _initialize_business_services(self) -> None:
        """Initialize business logic services."""
        # Resume service (depends on file service)
        from .resume_service import ResumeService
        resume_provider = ResumeServiceProvider(self._instances['file_service'])
        self.register_service('resume_service', resume_provider)
        await resume_provider.initialize()
        self._instances['resume_service'] = resume_provider.get_service()
        
        # Application service (depends on file service)
        from .application_service import ApplicationService
        app_provider = ApplicationServiceProvider(self._instances['file_service'])
        self.register_service('application_service', app_provider)
        await app_provider.initialize()
        self._instances['application_service'] = app_provider.get_service()
        
        # Cover letter service (depends on AI service)
        from .cover_letter_service import CoverLetterService
        cover_provider = CoverLetterServiceProvider(self._instances['ai_service'])
        self.register_service('cover_letter_service', cover_provider)
        await cover_provider.initialize()
        self._instances['cover_letter_service'] = cover_provider.get_service()
        
        # Job search service (no dependencies)
        from .job_search_service import JobSearchService
        job_provider = JobSearchServiceProvider()
        self.register_service('job_search_service', job_provider)
        await job_provider.initialize()
        self._instances['job_search_service'] = job_provider.get_service()
        
        # Job application service (no dependencies)
        from .job_application_service import MultiPlatformJobApplicationService
        job_app_provider = JobApplicationServiceProvider()
        self.register_service('job_application_service', job_app_provider)
        await job_app_provider.initialize()
        self._instances['job_application_service'] = job_app_provider.get_service()
    
    async def get_service(self, name: str) -> Any:
        """Get a service instance by name."""
        if not self._initialized:
            self._logger.info("Service registry not initialized, initializing now...")
            await self.initialize()
        
        if name not in self._instances:
            raise KeyError(f"Service '{name}' not found")
        
        return self._instances[name]
    
    # Convenience methods for type-safe service access
    async def get_ai_service(self) -> AIService:
        """Get the AI service instance."""
        return await self.get_service('ai_service')
    
    async def get_file_service(self) -> FileService:
        """Get the file service instance."""
        return await self.get_service('file_service')
    
    async def get_resume_service(self) -> ResumeService:
        """Get the resume service instance."""
        return await self.get_service('resume_service')
    
    async def get_application_service(self) -> ApplicationService:
        """Get the application service instance."""
        return await self.get_service('application_service')
    
    async def get_cover_letter_service(self) -> CoverLetterService:
        """Get the cover letter service instance."""
        return await self.get_service('cover_letter_service')
    
    async def get_job_search_service(self) -> JobSearchService:
        """Get the job search service instance."""
        return await self.get_service('job_search_service')
    
    async def get_job_application_service(self) -> JobApplicationService:
        """Get the job application service instance."""
        return await self.get_service('job_application_service')
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of all services."""
        if not self._initialized:
            await self.initialize()
        
        health_status = {
            "service_registry": "healthy",
            "services": {}
        }
        
        try:
            # Check each service
            for name, instance in self._instances.items():
                try:
                    if hasattr(instance, 'health_check'):
                        service_health = await instance.health_check()
                        health_status["services"][name] = service_health
                    elif hasattr(instance, 'is_available'):
                        available = await instance.is_available()
                        health_status["services"][name] = {
                            "status": "healthy" if available else "degraded",
                            "available": available
                        }
                    else:
                        health_status["services"][name] = {
                            "status": "healthy",
                            "available": True
                        }
                except Exception as e:
                    health_status["services"][name] = {
                        "status": "unhealthy",
                        "available": False,
                        "error": str(e)
                    }
            
        except Exception as e:
            self._logger.error(f"Error during health check: {e}", exc_info=True)
            health_status["service_registry"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def shutdown(self) -> None:
        """Shutdown all services gracefully."""
        try:
            self._logger.info("Shutting down service registry...")
            
            # Cleanup services in reverse dependency order
            for name, provider in reversed(list(self._services.items())):
                try:
                    await provider.cleanup()
                    self._logger.debug(f"Cleaned up {name}")
                except Exception as e:
                    self._logger.error(f"Error cleaning up {name}: {e}")
            
            self._instances.clear()
            self._services.clear()
            self._initialized = False
            
            self._logger.info("Service registry shut down successfully")
            
        except Exception as e:
            self._logger.error(f"Error shutting down service registry: {e}", exc_info=True)


# Service Provider Implementations
class LocalFileServiceProvider(ServiceProvider):
    """Provider for local file service."""
    
    def get_service(self) -> FileService:
        return self._service
    
    async def initialize(self) -> None:
        from .local_file_service import LocalFileService
        self._service = LocalFileService()
    
    async def cleanup(self) -> None:
        if hasattr(self._service, 'cleanup'):
            await self._service.cleanup()


class GeminiAIProvider(ServiceProvider):
    """Provider for Gemini AI service."""
    
    def get_service(self) -> AIService:
        return self._service
    
    async def initialize(self) -> None:
        from .gemini_ai_service import GeminiAIService
        self._service = GeminiAIService()
    
    async def cleanup(self) -> None:
        if hasattr(self._service, 'cleanup'):
            await self._service.cleanup()


class ResumeServiceProvider(ServiceProvider):
    """Provider for resume service."""
    
    def __init__(self, file_service: FileService):
        self.file_service = file_service
    
    def get_service(self) -> ResumeService:
        return self._service
    
    async def initialize(self) -> None:
        from .resume_service import ResumeService
        self._service = ResumeService(self.file_service)
    
    async def cleanup(self) -> None:
        if hasattr(self._service, 'cleanup'):
            await self._service.cleanup()


class ApplicationServiceProvider(ServiceProvider):
    """Provider for application service."""
    
    def __init__(self, file_service: FileService):
        self.file_service = file_service
    
    def get_service(self) -> ApplicationService:
        return self._service
    
    async def initialize(self) -> None:
        from .application_service import ApplicationService
        self._service = ApplicationService(self.file_service)
    
    async def cleanup(self) -> None:
        if hasattr(self._service, 'cleanup'):
            await self._service.cleanup()


class CoverLetterServiceProvider(ServiceProvider):
    """Provider for cover letter service."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    def get_service(self) -> CoverLetterService:
        return self._service
    
    async def initialize(self) -> None:
        from .cover_letter_service import CoverLetterService
        self._service = CoverLetterService(self.ai_service)
    
    async def cleanup(self) -> None:
        if hasattr(self._service, 'cleanup'):
            await self._service.cleanup()


class JobSearchServiceProvider(ServiceProvider):
    """Provider for job search service."""
    
    def get_service(self) -> JobSearchService:
        return self._service
    
    async def initialize(self) -> None:
        from .job_search_service import JobSearchService
        self._service = JobSearchService()
        # Initialize the service to check JobSpy availability
        await self._service.initialize()
    
    async def cleanup(self) -> None:
        if hasattr(self._service, 'cleanup'):
            await self._service.cleanup()


class JobApplicationServiceProvider(ServiceProvider):
    """Provider for job application service."""
    
    def get_service(self) -> JobApplicationService:
        return self._service
    
    async def initialize(self) -> None:
        from .job_application_service import MultiPlatformJobApplicationService
        self._service = MultiPlatformJobApplicationService()
        await self._service.initialize()
    
    async def cleanup(self) -> None:
        if hasattr(self._service, 'cleanup'):
            await self._service.cleanup()


# Global service registry instance
service_registry = ServiceRegistry()
