"""Service registry for dependency injection in the AI Job Application Assistant."""

from typing import Optional, Dict, Any
from ..core.ai_service import AIService
from ..core.file_service import FileService
from ..core.resume_service import ResumeService
from ..core.application_service import ApplicationService
from ..utils.logger import get_logger

from .gemini_ai_service import GeminiAIService
from .local_file_service import LocalFileService
from .file_based_resume_service import FileBasedResumeService
from .memory_based_application_service import MemoryBasedApplicationService
from .jobspy_job_service import JobSpyJobService


class ServiceRegistry:
    """Registry for managing service dependencies and dependency injection."""
    
    def __init__(self):
        """Initialize the service registry."""
        self.logger = get_logger(__name__)
        self._services: Dict[str, Any] = {}
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize all services with proper dependencies."""
        if self._initialized:
            return
        
        try:
            self.logger.info("Initializing service registry...")
            
            # Initialize services in dependency order
            
            # 1. File service (no dependencies)
            file_service = LocalFileService()
            self._services['file_service'] = file_service
            
            # 2. AI service (no dependencies)
            ai_service = GeminiAIService()
            self._services['ai_service'] = ai_service
            
            # 3. Resume service (depends on file service)
            resume_service = FileBasedResumeService(file_service)
            self._services['resume_service'] = resume_service
            
            # 4. Application service (no dependencies for memory-based)
            application_service = MemoryBasedApplicationService()
            self._services['application_service'] = application_service
            
            # 5. Job search service (no dependencies)
            job_search_service = JobSpyJobService()
            self._services['job_search_service'] = job_search_service
            
            self._initialized = True
            self.logger.info("Service registry initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing service registry: {e}", exc_info=True)
            raise
    
    def get_ai_service(self) -> AIService:
        """Get the AI service instance."""
        if not self._initialized:
            self.initialize()
        return self._services['ai_service']
    
    def get_file_service(self) -> FileService:
        """Get the file service instance."""
        if not self._initialized:
            self.initialize()
        return self._services['file_service']
    
    def get_resume_service(self) -> ResumeService:
        """Get the resume service instance."""
        if not self._initialized:
            self.initialize()
        return self._services['resume_service']
    
    def get_application_service(self) -> ApplicationService:
        """Get the application service instance."""
        if not self._initialized:
            self.initialize()
        return self._services['application_service']
    
    def get_job_search_service(self):
        """Get the job search service instance."""
        if not self._initialized:
            self.initialize()
        return self._services['job_search_service']
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of all services."""
        if not self._initialized:
            self.initialize()
        
        health_status = {
            "service_registry": "healthy",
            "services": {}
        }
        
        try:
            # Check AI service
            ai_service = self.get_ai_service()
            ai_available = await ai_service.is_available()
            health_status["services"]["ai_service"] = {
                "status": "healthy" if ai_available else "degraded",
                "available": ai_available
            }
            
            # Check file service (always available for local)
            health_status["services"]["file_service"] = {
                "status": "healthy",
                "available": True
            }
            
            # Check resume service
            resume_service = self.get_resume_service()
            resumes = await resume_service.get_all_resumes()
            health_status["services"]["resume_service"] = {
                "status": "healthy",
                "available": True,
                "resume_count": len(resumes)
            }
            
            # Check application service
            application_service = self.get_application_service()
            apps = await application_service.get_all_applications()
            health_status["services"]["application_service"] = {
                "status": "healthy",
                "available": True,
                "application_count": len(apps)
            }
            
            # Check job search service
            job_search_service = self.get_job_search_service()
            job_search_available = await job_search_service.is_available()
            health_status["services"]["job_search_service"] = {
                "status": "healthy" if job_search_available else "degraded",
                "available": job_search_available
            }
            
        except Exception as e:
            self.logger.error(f"Error during health check: {e}", exc_info=True)
            health_status["service_registry"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    def shutdown(self) -> None:
        """Shutdown all services gracefully."""
        try:
            self.logger.info("Shutting down service registry...")
            
            # Perform any cleanup needed for services
            for service_name, service in self._services.items():
                if hasattr(service, 'shutdown'):
                    service.shutdown()
                    self.logger.debug(f"Shut down {service_name}")
            
            self._services.clear()
            self._initialized = False
            
            self.logger.info("Service registry shut down successfully")
            
        except Exception as e:
            self.logger.error(f"Error shutting down service registry: {e}", exc_info=True)


# Global service registry instance
service_registry = ServiceRegistry()
