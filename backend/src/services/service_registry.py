"""Unified service registry for dependency injection in the AI Job Application Assistant."""

from typing import Dict, Any, Optional
from loguru import logger
from abc import ABC, abstractmethod

from src.core.ai_service import AIService
from src.core.file_service import FileService
from src.core.resume_service import ResumeService
from src.core.application_service import ApplicationService
from src.core.job_search import JobSearchService
from src.core.cover_letter_service import CoverLetterService
from src.core.job_application import JobApplicationService
from src.core.auth_service import AuthService
from src.core.monitoring_service import MonitoringService
from src.core.export_service import ExportService
from src.services.email_service import EmailService
from src.services.push_service import PushService


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
            self._logger.error(
                f"Error initializing service registry: {e}", exc_info=True
            )
            raise

    async def _initialize_core_services(self) -> None:
        """Initialize core infrastructure services."""
        # Ensure database is initialized first (required by auth and monitoring services)
        from src.database.config import database_config

        if not database_config._initialized:
            self._logger.info("Initializing database for services...")
            await database_config.initialize()
            await database_config.create_tables()
            self._logger.info("Database initialized for services")

        # Auth service (no dependencies, but needs database)
        # Database is initialized

        # Email service (no dependencies)
        from src.services.email_service import EmailService

        email_provider = EmailServiceProvider()
        self.register_service("email_service", email_provider)
        await email_provider.initialize()
        self._instances["email_service"] = email_provider.get_service()

        # Mailgun provider (no dependencies, optional)
        try:
            mailgun_provider = MailgunProviderClass()
            self.register_service("mailgun_provider", mailgun_provider)
            await mailgun_provider.initialize()
            self._instances["mailgun_provider"] = mailgun_provider.get_service()
            if self._instances["mailgun_provider"]:
                self._logger.info("Mailgun provider initialized successfully")
        except Exception as e:
            self._logger.warning(
                f"Failed to initialize Mailgun provider: {e}. Continuing without Mailgun."
            )

        # Auth service (depends on email service)
        from src.services.auth_service import JWTAuthService

        auth_provider = JWTAuthServiceProvider(self._instances["email_service"])
        self.register_service("auth_service", auth_provider)
        await auth_provider.initialize()
        self._instances["auth_service"] = auth_provider.get_service()

        # File service (no dependencies)
        from src.services.local_file_service import LocalFileService

        file_provider = LocalFileServiceProvider()
        self.register_service("file_service", file_provider)
        await file_provider.initialize()
        self._instances["file_service"] = file_provider.get_service()

        # AI service (no dependencies) - Use unified service with multiple providers
        try:
            from src.services.unified_ai_service import UnifiedAIService

            ai_provider = UnifiedAIServiceProvider()
            self.register_service("ai_service", ai_provider)
            await ai_provider.initialize()
            self._instances["ai_service"] = ai_provider.get_service()
        except Exception as e:
            self._logger.warning(
                f"Failed to initialize unified AI service, falling back to Gemini: {e}"
            )
            # Fallback to Gemini-only service
            from src.services.gemini_ai_service import GeminiAIService

            ai_provider = GeminiAIProvider()
            self.register_service("ai_service", ai_provider)
            await ai_provider.initialize()
            self._instances["ai_service"] = ai_provider.get_service()

        # Monitoring service (no dependencies, but needs database)
        # Make this optional - if it fails, app can still run
        try:
            from src.services.monitoring_service import DatabaseMonitoringService

            monitoring_provider = MonitoringServiceProvider()
            self.register_service("monitoring_service", monitoring_provider)
            await monitoring_provider.initialize()
            self._instances["monitoring_service"] = monitoring_provider.get_service()
        except ImportError as e:
            self._logger.warning(
                f"Monitoring service not available: {e}. Continuing without monitoring."
            )
        except Exception as e:
            self._logger.warning(
                f"Failed to initialize monitoring service: {e}. Continuing without monitoring."
            )

    async def _initialize_business_services(self) -> None:
        """Initialize business logic services."""
        # Initialize repository factory
        from src.services.repository_factory import repository_factory

        await repository_factory.initialize()

        # Resume service (depends on file service)
        from src.services.resume_service import ResumeService

        resume_provider = ResumeServiceProvider(self._instances["file_service"])
        self.register_service("resume_service", resume_provider)
        await resume_provider.initialize()
        self._instances["resume_service"] = resume_provider.get_service()

        # Application service (depends on file service)
        from src.services.application_service import ApplicationService

        app_provider = ApplicationServiceProvider(self._instances["file_service"])
        self.register_service("application_service", app_provider)
        await app_provider.initialize()
        self._instances["application_service"] = app_provider.get_service()

        # Cover letter service (depends on AI service)
        from src.services.cover_letter_service import CoverLetterService

        cover_provider = CoverLetterServiceProvider(self._instances["ai_service"])
        self.register_service("cover_letter_service", cover_provider)
        await cover_provider.initialize()
        self._instances["cover_letter_service"] = cover_provider.get_service()

        # Job search service (no dependencies)
        from src.services.job_search_service import JobSearchService

        job_provider = JobSearchServiceProvider()
        self.register_service("job_search_service", job_provider)
        await job_provider.initialize()
        self._instances["job_search_service"] = job_provider.get_service()

        # Job application service (no dependencies)
        from src.services.job_application_service import (
            MultiPlatformJobApplicationService,
        )

        job_app_provider = JobApplicationServiceProvider()
        self.register_service("job_application_service", job_app_provider)
        await job_app_provider.initialize()
        self._instances["job_application_service"] = job_app_provider.get_service()

        # Export service (no dependencies)
        export_provider = ExportServiceProvider()
        self.register_service("export_service", export_provider)
        await export_provider.initialize()
        self._instances["export_service"] = export_provider.get_service()

        # Scheduler service (no dependencies)
        try:
            from src.services.scheduler_service import SchedulerService

            scheduler_provider = SchedulerServiceProvider()
            self.register_service("scheduler_service", scheduler_provider)
            await scheduler_provider.initialize()
            self._instances["scheduler_service"] = scheduler_provider.get_service()
        except Exception as e:
            self._logger.warning(
                f"Failed to initialize scheduler service: {e}. Continuing without scheduling."
            )

        # Notification service (depends on email service)
        try:
            # Push service (optional, depends on database)
            try:
                push_provider = PushServiceProvider()
                self.register_service("push_service", push_provider)
                await push_provider.initialize()
                self._instances["push_service"] = push_provider.get_service()
            except Exception as e:
                self._logger.warning(
                    f"Failed to initialize push service: {e}. Continuing without push notifications."
                )

            from src.services.notification_service import NotificationService

            notification_provider = NotificationServiceProvider(
                email_service=self._instances["email_service"],
                push_service=self._instances.get("push_service"),
            )
            self.register_service("notification_service", notification_provider)
            await notification_provider.initialize()
            self._instances["notification_service"] = (
                notification_provider.get_service()
            )
        except Exception as e:
            self._logger.warning(
                f"Failed to initialize notification service: {e}. Continuing without notifications."
            )

        # Resume builder service (no dependencies)
        try:
            from src.services.resume_builder_service import ResumeBuilderService

            resume_builder_provider = ResumeBuilderServiceProvider()
            self.register_service("resume_builder_service", resume_builder_provider)
            await resume_builder_provider.initialize()
            self._instances["resume_builder_service"] = (
                resume_builder_provider.get_service()
            )
        except Exception as e:
            self._logger.warning(
                f"Failed to initialize resume builder service: {e}. Continuing without resume building."
            )

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
        return await self.get_service("ai_service")

    async def get_file_service(self) -> FileService:
        """Get the file service instance."""
        return await self.get_service("file_service")

    async def get_resume_service(self) -> ResumeService:
        """Get the resume service instance."""
        return await self.get_service("resume_service")

    async def get_application_service(self) -> ApplicationService:
        """Get the application service instance."""
        return await self.get_service("application_service")

    async def get_cover_letter_service(self) -> CoverLetterService:
        """Get the cover letter service instance."""
        return await self.get_service("cover_letter_service")

    async def get_job_search_service(self) -> JobSearchService:
        """Get the job search service instance."""
        return await self.get_service("job_search_service")

    async def get_job_application_service(self) -> JobApplicationService:
        """Get the job application service instance."""
        return await self.get_service("job_application_service")

    async def get_auth_service(self) -> AuthService:
        """Get the authentication service instance."""
        return await self.get_service("auth_service")

    async def get_monitoring_service(self) -> MonitoringService:
        """Get the monitoring service instance."""
        return await self.get_service("monitoring_service")

    async def get_export_service(self) -> ExportService:
        """Get the export service instance."""
        return await self.get_service("export_service")

    async def get_email_service(self) -> EmailService:
        """Get the email service instance."""
        return await self.get_service("email_service")

    async def get_scheduler_service(self):
        """Get the scheduler service instance."""
        return await self.get_service("scheduler_service")

    async def get_notification_service(self):
        """Get the notification service instance."""
        return await self.get_service("notification_service")

    async def get_push_service(self) -> PushService:
        """Get the push notification service instance."""
        return await self.get_service("push_service")

    async def get_resume_builder_service(self):
        """Get the resume builder service instance."""
        return await self.get_service("resume_builder_service")

    async def get_mailgun_provider(self):
        """Get the mailgun provider instance (may return None if not configured)."""
        try:
            return await self.get_service("mailgun_provider")
        except KeyError:
            # Mailgun provider not registered, return None
            return None

    def get_monitoring_service_sync(self) -> MonitoringService:
        """Get the monitoring service instance synchronously (for middleware)."""
        if not self._initialized:
            raise RuntimeError("Service registry not initialized")
        if "monitoring_service" not in self._instances:
            raise KeyError("Monitoring service not found")
        return self._instances["monitoring_service"]

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of all services."""
        if not self._initialized:
            await self.initialize()

        health_status = {"service_registry": "healthy", "services": {}}

        try:
            # Check each service
            for name, instance in self._instances.items():
                try:
                    if hasattr(instance, "health_check"):
                        service_health = await instance.health_check()
                        health_status["services"][name] = service_health
                    elif hasattr(instance, "is_available"):
                        available = await instance.is_available()
                        health_status["services"][name] = {
                            "status": "healthy" if available else "degraded",
                            "available": available,
                        }
                    else:
                        health_status["services"][name] = {
                            "status": "healthy",
                            "available": True,
                        }
                except Exception as e:
                    health_status["services"][name] = {
                        "status": "unhealthy",
                        "available": False,
                        "error": str(e),
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
            self._logger.error(
                f"Error shutting down service registry: {e}", exc_info=True
            )


# Service Provider Implementations
class LocalFileServiceProvider(ServiceProvider):
    """Provider for local file service."""

    def get_service(self) -> FileService:
        return self._service

    async def initialize(self) -> None:
        from src.services.local_file_service import LocalFileService

        self._service = LocalFileService()

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class UnifiedAIServiceProvider(ServiceProvider):
    """Provider for unified AI service with multiple providers."""

    def get_service(self) -> AIService:
        return self._service

    async def initialize(self) -> None:
        from src.services.unified_ai_service import UnifiedAIService

        self._service = UnifiedAIService()
        await self._service.initialize()

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class GeminiAIProvider(ServiceProvider):
    """Provider for Gemini AI service (fallback)."""

    def get_service(self) -> AIService:
        return self._service

    async def initialize(self) -> None:
        from src.services.gemini_ai_service import GeminiAIService

        self._service = GeminiAIService()

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class ResumeServiceProvider(ServiceProvider):
    """Provider for resume service."""

    def __init__(self, file_service: FileService):
        self.file_service = file_service
        self._logger = logger.bind(module="ResumeServiceProvider")

    def get_service(self) -> ResumeService:
        return self._service

    async def initialize(self) -> None:
        from src.services.resume_service import ResumeService
        from src.services.repository_factory import repository_factory
        from src.database.repositories.resume_repository import ResumeRepository

        # Try to create repository if database is available
        repository = None
        if repository_factory.is_available():
            try:
                repository = await repository_factory.create_repository(
                    ResumeRepository
                )
            except Exception as e:
                self._logger.warning(
                    f"Could not create resume repository, using in-memory storage: {e}"
                )

        self._service = ResumeService(self.file_service, repository)

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class ApplicationServiceProvider(ServiceProvider):
    """Provider for application service."""

    def __init__(self, file_service: FileService):
        self.file_service = file_service
        self._logger = logger.bind(module="ApplicationServiceProvider")

    def get_service(self) -> ApplicationService:
        return self._service

    async def initialize(self) -> None:
        from src.services.application_service import ApplicationService
        from src.services.repository_factory import repository_factory
        from src.database.repositories.application_repository import (
            ApplicationRepository,
        )

        # Try to create repository if database is available
        repository = None
        if repository_factory.is_available():
            try:
                repository = await repository_factory.create_repository(
                    ApplicationRepository
                )
            except Exception as e:
                self._logger.warning(
                    f"Could not create application repository, using in-memory storage: {e}"
                )

        self._service = ApplicationService(self.file_service, repository)

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class CoverLetterServiceProvider(ServiceProvider):
    """Provider for cover letter service."""

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self._logger = logger.bind(module="CoverLetterServiceProvider")

    def get_service(self) -> CoverLetterService:
        return self._service

    async def initialize(self) -> None:
        from src.services.cover_letter_service import CoverLetterService
        from src.services.repository_factory import repository_factory
        from src.database.repositories.cover_letter_repository import (
            CoverLetterRepository,
        )

        # Try to create repository if database is available
        repository = None
        if repository_factory.is_available():
            try:
                repository = await repository_factory.create_repository(
                    CoverLetterRepository
                )
            except Exception as e:
                self._logger.warning(
                    f"Could not create cover letter repository, using in-memory storage: {e}"
                )

        self._service = CoverLetterService(self.ai_service, repository)

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class JobSearchServiceProvider(ServiceProvider):
    """Provider for job search service."""

    def get_service(self) -> JobSearchService:
        return self._service

    async def initialize(self) -> None:
        from src.services.job_search_service import JobSearchService

        self._service = JobSearchService()
        # Initialize the service to check JobSpy availability
        await self._service.initialize()

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class JobApplicationServiceProvider(ServiceProvider):
    """Provider for job application service."""

    def get_service(self) -> JobApplicationService:
        return self._service

    async def initialize(self) -> None:
        from src.services.job_application_service import (
            MultiPlatformJobApplicationService,
        )

        self._service = MultiPlatformJobApplicationService()
        await self._service.initialize()

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class JWTAuthServiceProvider(ServiceProvider):
    """Provider for JWT authentication service."""

    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    def get_service(self) -> AuthService:
        return self._service

    async def initialize(self) -> None:
        from src.services.auth_service import JWTAuthService

        self._service = JWTAuthService(self.email_service)
        await self._service.initialize()

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class MonitoringServiceProvider(ServiceProvider):
    """Provider for monitoring service."""

    def __init__(self):
        self._logger = logger.bind(module="MonitoringServiceProvider")

    def get_service(self) -> MonitoringService:
        return self._service

    async def initialize(self) -> None:
        from src.services.monitoring_service import DatabaseMonitoringService

        self._service = DatabaseMonitoringService()
        # Initialize default alert rules
        await self._initialize_default_alert_rules()

    async def _initialize_default_alert_rules(self) -> None:
        """Initialize default alert rules."""
        try:
            rules = await self._service.get_alert_rules()
            existing_rule_names = {rule.get("rule_name") for rule in rules}

            default_rules = [
                {
                    "rule_name": "High Error Rate",
                    "metric_name": "error_rate",
                    "threshold": 5.0,
                    "condition": "gt",
                    "cooldown_seconds": 300,
                },
                {
                    "rule_name": "Slow Response Time",
                    "metric_name": "api.response_time",
                    "threshold": 1000.0,  # 1 second in milliseconds
                    "condition": "gt",
                    "cooldown_seconds": 300,
                },
                {
                    "rule_name": "Slow Database Query",
                    "metric_name": "database.query_time",
                    "threshold": 100.0,  # 100ms in milliseconds
                    "condition": "gt",
                    "cooldown_seconds": 300,
                },
            ]

            for rule_config in default_rules:
                if rule_config["rule_name"] not in existing_rule_names:
                    try:
                        await self._service.create_alert_rule(**rule_config)
                        self._logger.info(
                            f"Created default alert rule: {rule_config['rule_name']}"
                        )
                    except Exception as e:
                        self._logger.warning(
                            f"Could not create default alert rule {rule_config['rule_name']}: {e}"
                        )
        except Exception as e:
            self._logger.warning(f"Could not initialize default alert rules: {e}")

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class ExportServiceProvider(ServiceProvider):
    """Provider for export service."""

    def get_service(self) -> ExportService:
        return self._service

    async def initialize(self) -> None:
        from src.services.export_service import MultiFormatExportService

        self._service = MultiFormatExportService()

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


# Global service registry instance
service_registry = ServiceRegistry()


class EmailServiceProvider(ServiceProvider):
    """Provider for email service."""

    def get_service(self) -> EmailService:
        return self._service

    async def initialize(self) -> None:
        from src.services.email_service import EmailService

        self._service = EmailService()

    async def cleanup(self) -> None:
        pass


class SchedulerServiceProvider(ServiceProvider):
    """Provider for scheduler service."""

    def get_service(self):
        return self._service

    async def initialize(self) -> None:
        from src.services.scheduler_service import SchedulerService

        self._service = SchedulerService()
        await self._service.initialize()

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()
        if hasattr(self._service, "stop"):
            await self._service.stop()


class NotificationServiceProvider(ServiceProvider):
    """Provider for notification service."""

    def __init__(
        self, email_service: EmailService, push_service: Optional[PushService] = None
    ):
        self.email_service = email_service
        self.push_service = push_service

    def get_service(self):
        return self._service

    async def initialize(self) -> None:
        from src.services.notification_service import NotificationService

        self._service = NotificationService(
            email_service=self.email_service, push_service=self.push_service
        )
        await self._service.initialize()

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class ResumeBuilderServiceProvider(ServiceProvider):
    """Provider for resume builder service."""

    def get_service(self):
        return self._service

    async def initialize(self) -> None:
        from src.services.resume_builder_service import ResumeBuilderService

        self._service = ResumeBuilderService()
        await self._service.initialize()

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class MailgunProviderClass(ServiceProvider):
    """Provider for Mailgun email provider."""

    def get_service(self):
        return self._service

    async def initialize(self) -> None:
        from src.services.mailgun_client import create_mailgun_provider

        self._service = create_mailgun_provider()
        if self._service is None:
            self._logger.info(
                "Mailgun not configured, skipping provider initialization"
            )

    async def cleanup(self) -> None:
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()
        elif hasattr(self._service, "close"):
            import asyncio

            try:
                asyncio.get_event_loop().run_until_complete(self._service.close())
            except Exception:
                pass


class PushServiceProvider(ServiceProvider):
    """Provider for Web Push notification service."""

    def get_service(self) -> PushService:
        return self._service

    async def initialize(self) -> None:
        from src.services.push_service import PushService

        self._service = PushService()

    async def cleanup(self) -> None:
        pass
