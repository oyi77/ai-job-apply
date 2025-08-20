"""Database-backed service registry for dependency injection."""

import asyncio
from typing import Optional, Dict, Any
from ..core.ai_service import AIService
from ..core.file_service import FileService
from ..core.resume_service import ResumeService
from ..core.application_service import ApplicationService
from ..utils.logger import get_logger
from ..database.config import database_config, init_database, close_database
from ..database.repositories import (
    ApplicationRepository, 
    ResumeRepository, 
    CoverLetterRepository, 
    FileRepository
)

from .gemini_ai_service import GeminiAIService
from .local_file_service import LocalFileService
from .file_based_resume_service import FileBasedResumeService
from .memory_based_application_service import MemoryBasedApplicationService
# from .jobspy_job_service import JobSpyJobService


class DatabaseBackedResumeService(FileBasedResumeService):
    """Database-backed resume service."""
    
    def __init__(self, file_service: FileService):
        """Initialize with file service."""
        super().__init__(file_service)
        self.logger = get_logger(__name__)
        self._repository = None
    
    async def _get_repository(self) -> ResumeRepository:
        """Get repository instance."""
        if self._repository is None:
            session = await database_config.get_session()
            self._repository = ResumeRepository(session)
        return self._repository


class DatabaseBackedApplicationService(MemoryBasedApplicationService):
    """Database-backed application service."""
    
    def __init__(self):
        """Initialize database-backed application service."""
        # Don't call super().__init__() to avoid loading sample data
        self.logger = get_logger(__name__)
        self._repository = None
    
    async def _get_repository(self) -> ApplicationRepository:
        """Get repository instance."""
        if self._repository is None:
            session = await database_config.get_session()
            self._repository = ApplicationRepository(session)
        return self._repository
    
    async def create_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new job application using database."""
        try:
            from ..models.application import JobApplication, ApplicationStatus
            
            # Create application model
            application = JobApplication(
                job_id=application_data["job_id"],
                job_title=application_data["job_title"],
                company=application_data["company"],
                status=ApplicationStatus(application_data.get("status", "draft")),
                notes=application_data.get("notes"),
                resume_path=application_data.get("resume_path"),
                cover_letter_path=application_data.get("cover_letter_path")
            )
            
            # Save to database
            repository = await self._get_repository()
            saved_application = await repository.create(application)
            
            self.logger.info(f"Created application: {saved_application.job_title} at {saved_application.company}")
            return saved_application.model_dump()
            
        except Exception as e:
            self.logger.error(f"Error creating application: {e}", exc_info=True)
            raise
    
    async def get_all_applications(self, limit: Optional[int] = None) -> list:
        """Get all applications from database."""
        try:
            repository = await self._get_repository()
            applications = await repository.get_all(limit=limit)
            
            return [app.model_dump() for app in applications]
            
        except Exception as e:
            self.logger.error(f"Error getting applications: {e}", exc_info=True)
            return []
    
    async def get_application_stats(self) -> Dict[str, Any]:
        """Get application statistics from database."""
        try:
            repository = await self._get_repository()
            return await repository.get_statistics()
            
        except Exception as e:
            self.logger.error(f"Error getting application stats: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def get_application(self, application_id: str):
        """Get application by ID from database."""
        try:
            repository = await self._get_repository()
            application = await repository.get_by_id(application_id)
            return application.model_dump() if application else None
            
        except Exception as e:
            self.logger.error(f"Error getting application {application_id}: {e}", exc_info=True)
            return None
    
    async def update_application(self, application_id: str, updates):
        """Update application in database."""
        try:
            repository = await self._get_repository()
            application = await repository.get_by_id(application_id)
            if not application:
                return None
            
            # Update fields
            for field, value in updates.model_dump(exclude_unset=True).items():
                if hasattr(application, field):
                    setattr(application, field, value)
            
            # Save updated application
            updated_application = await repository.update(application)
            return updated_application.model_dump()
            
        except Exception as e:
            self.logger.error(f"Error updating application {application_id}: {e}", exc_info=True)
            return None
    
    async def delete_application(self, application_id: str) -> bool:
        """Delete application from database."""
        try:
            repository = await self._get_repository()
            return await repository.delete(application_id)
            
        except Exception as e:
            self.logger.error(f"Error deleting application {application_id}: {e}", exc_info=True)
            return False


class DatabaseServiceRegistry:
    """Registry for managing database-backed service dependencies."""
    
    def __init__(self, use_database: bool = True):
        """Initialize the service registry."""
        self.logger = get_logger(__name__)
        self._services: Dict[str, Any] = {}
        self._initialized = False
        self._use_database = use_database
        self._database_initialized = False
    
    async def initialize(self) -> None:
        """Initialize all services with proper dependencies."""
        if self._initialized:
            return
        
        try:
            self.logger.info("Initializing database service registry...")
            
            # Initialize database if using database-backed services
            if self._use_database:
                await self._initialize_database()
            
            # Initialize services in dependency order
            
            # 1. File service (no dependencies)
            file_service = LocalFileService()
            self._services['file_service'] = file_service
            
            # 2. AI service (no dependencies)
            ai_service = GeminiAIService()
            self._services['ai_service'] = ai_service
            
            # 3. Resume service (depends on file service)
            if self._use_database:
                resume_service = DatabaseBackedResumeService(file_service)
            else:
                resume_service = FileBasedResumeService(file_service)
            self._services['resume_service'] = resume_service
            
            # 4. Application service
            if self._use_database:
                application_service = DatabaseBackedApplicationService()
            else:
                application_service = MemoryBasedApplicationService()
            self._services['application_service'] = application_service
            
            # 5. Job search service (no dependencies)
            # job_search_service = JobSpyJobService()
            # self._services['job_search_service'] = job_search_service
            
            # Temporary mock job search service for testing
            class MockJobSearchService:
                async def search_jobs(self, query: str, location: str = None, limit: int = 10):
                    return [
                        {
                            "id": "1", 
                            "title": "Software Engineer", 
                            "company": "Tech Corp", 
                            "location": "Remote",
                            "url": "https://techcorp.com/careers/software-engineer",
                            "portal": "LinkedIn",
                            "description": "We are looking for a talented software engineer...",
                            "requirements": ["Python", "JavaScript", "React"],
                            "salary_range": "$80,000 - $120,000",
                            "job_type": "full_time",
                            "experience_level": "mid"
                        },
                        {
                            "id": "2", 
                            "title": "Data Scientist", 
                            "company": "AI Inc", 
                            "location": "San Francisco",
                            "url": "https://aiinc.com/careers/data-scientist",
                            "portal": "Indeed",
                            "description": "Join our AI research team...",
                            "requirements": ["Python", "Machine Learning", "Statistics"],
                            "salary_range": "$100,000 - $150,000",
                            "job_type": "full_time",
                            "experience_level": "senior"
                        }
                    ]
                
                async def get_job_details(self, job_id: str, platform: str = None):
                    return {
                        "id": job_id,
                        "title": "Software Engineer",
                        "company": "Tech Corp",
                        "location": "Remote",
                        "url": "https://techcorp.com/careers/software-engineer",
                        "portal": "LinkedIn",
                        "description": "We are looking for a talented software engineer...",
                        "requirements": ["Python", "JavaScript", "React"],
                        "salary_range": "$80,000 - $120,000",
                        "job_type": "full_time",
                        "experience_level": "mid"
                    }
                
                async def is_available(self):
                    return True
            
            job_search_service = MockJobSearchService()
            self._services['job_search_service'] = job_search_service
            
            self._initialized = True
            self.logger.info("Database service registry initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing service registry: {e}", exc_info=True)
            raise
    
    async def _initialize_database(self) -> None:
        """Initialize database connection and tables."""
        if self._database_initialized:
            return
        
        try:
            self.logger.info("Initializing database...")
            await init_database()
            self._database_initialized = True
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}", exc_info=True)
            # Fallback to non-database mode
            self._use_database = False
            self.logger.warning("Falling back to in-memory services")
    
    def get_ai_service(self) -> AIService:
        """Get the AI service instance."""
        if not self._initialized:
            # For synchronous access, we need to handle async initialization
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, we can't call run()
                # The caller should use await initialize() first
                if not self._initialized:
                    raise RuntimeError("Service registry not initialized. Call await initialize() first.")
            else:
                loop.run_until_complete(self.initialize())
        return self._services['ai_service']
    
    def get_file_service(self) -> FileService:
        """Get the file service instance."""
        if not self._initialized:
            loop = asyncio.get_event_loop()
            if not loop.is_running():
                loop.run_until_complete(self.initialize())
            elif not self._initialized:
                raise RuntimeError("Service registry not initialized. Call await initialize() first.")
        return self._services['file_service']
    
    def get_resume_service(self) -> ResumeService:
        """Get the resume service instance."""
        if not self._initialized:
            loop = asyncio.get_event_loop()
            if not loop.is_running():
                loop.run_until_complete(self.initialize())
            elif not self._initialized:
                raise RuntimeError("Service registry not initialized. Call await initialize() first.")
        return self._services['resume_service']
    
    def get_application_service(self) -> ApplicationService:
        """Get the application service instance."""
        if not self._initialized:
            loop = asyncio.get_event_loop()
            if not loop.is_running():
                loop.run_until_complete(self.initialize())
            elif not self._initialized:
                raise RuntimeError("Service registry not initialized. Call await initialize() first.")
        return self._services['application_service']
    
    def get_job_search_service(self):
        """Get the job search service instance."""
        if not self._initialized:
            loop = asyncio.get_event_loop()
            if not loop.is_running():
                loop.run_until_complete(self.initialize())
            elif not self._initialized:
                raise RuntimeError("Service registry not initialized. Call await initialize() first.")
        return self._services['job_search_service']
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of all services."""
        if not self._initialized:
            await self.initialize()
        
        health_status = {
            "service_registry": "healthy",
            "database_mode": self._use_database,
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
            
            # Check database health if using database
            if self._use_database and self._database_initialized:
                try:
                    # Test database connection
                    session = await database_config.get_session()
                    await session.close()
                    health_status["database"] = {
                        "status": "healthy",
                        "available": True
                    }
                except Exception as db_error:
                    health_status["database"] = {
                        "status": "unhealthy",
                        "available": False,
                        "error": str(db_error)
                    }
            
        except Exception as e:
            self.logger.error(f"Error during health check: {e}", exc_info=True)
            health_status["service_registry"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def shutdown(self) -> None:
        """Shutdown all services gracefully."""
        try:
            self.logger.info("Shutting down database service registry...")
            
            # Perform any cleanup needed for services
            for service_name, service in self._services.items():
                if hasattr(service, 'shutdown'):
                    service.shutdown()
                    self.logger.debug(f"Shut down {service_name}")
            
            # Close database if initialized
            if self._database_initialized:
                await close_database()
                self._database_initialized = False
                self.logger.debug("Database connection closed")
            
            self._services.clear()
            self._initialized = False
            
            self.logger.info("Database service registry shut down successfully")
            
        except Exception as e:
            self.logger.error(f"Error shutting down service registry: {e}", exc_info=True)


# Global database service registry instance
database_service_registry = DatabaseServiceRegistry(use_database=True)
