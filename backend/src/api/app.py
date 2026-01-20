"""FastAPI application and API endpoints for the AI Job Application Assistant."""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBearer
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.config import config
from src.models.job import JobSearchRequest, JobSearchResponse
from src.models.resume import ResumeOptimizationRequest, ResumeOptimizationResponse
from src.models.cover_letter import CoverLetterRequest, CoverLetter
from src.models.application import JobApplication, ApplicationUpdateRequest
from src.utils.logger import get_logger
from src.services.service_registry import service_registry
from src.middleware.response_middleware import add_response_wrapper_middleware
from src.middleware.query_performance import setup_query_performance_monitoring
from src.database.config import database_config

# Initialize logger
logger = get_logger(__name__)

# Security
security = HTTPBearer(auto_error=False)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AI Job Application Assistant",
        description="An AI-powered assistant for job searching, resume optimization, and application management",
        version="1.0.0",
        docs_url="/docs" if config.DEBUG else None,
        redoc_url="/redoc" if config.DEBUG else None,
        redirect_slashes=False,  # Allow both /endpoint and /endpoint/ to work
    )

    # Initialize rate limiter (always create, but may be configured to not limit)
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter

    # Add rate limit exception handler
    from fastapi.responses import JSONResponse

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        """Handle rate limit exceeded exceptions."""
        return JSONResponse(
            status_code=429, content={"detail": f"Rate limit exceeded: {exc.detail}"}
        )

    if not config.rate_limit_enabled:
        logger.info("Rate limiting is disabled in configuration.")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add Security Headers Middleware
    from src.middleware.security_headers import SecurityHeadersMiddleware

    app.add_middleware(SecurityHeadersMiddleware)

    # Add Security Logging Middleware
    from src.middleware.security_logging import SecurityLoggingMiddleware

    app.add_middleware(SecurityLoggingMiddleware)

    # Response wrapper middleware disabled - using manual wrapping in endpoints
    # add_response_wrapper_middleware(app)

    # Mount static files if directory exists
    static_dir = Path("static")
    if static_dir.exists() and static_dir.is_dir():
        app.mount("/static", StaticFiles(directory="static"), name="static")

    # Include routers - handle import errors gracefully
    try:
        from src.api.v1.auth import router as auth_router
        from src.api.v1.jobs import router as jobs_router
        from src.api.v1.resumes import router as resumes_router
        from src.api.v1.applications import router as applications_router
        from src.api.v1.ai import router as ai_router
        from src.api.v1.cover_letters import router as cover_letters_router
        from src.api.v1.job_applications import router as job_applications_router
        from src.api.v1.monitoring import router as monitoring_router
        from src.api.v1.exports import router as exports_router
        from src.api.v1.files import router as files_router
        from src.api.v1.config import router as config_router
        from src.api.v1.cache import router as cache_router
        from src.api.v1.analytics import router as analytics_router
        from src.api.v1.ai_config import router as ai_config_router
        from src.api.v1.automation import router as automation_router
        from src.api.v1.scheduler import router as scheduler_router
        from src.api.v1.resume_builder import router as resume_builder_router

        app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
        app.include_router(jobs_router, prefix="/api/v1/jobs", tags=["jobs"])
        app.include_router(resumes_router, prefix="/api/v1/resumes", tags=["resumes"])
        app.include_router(
            applications_router, prefix="/api/v1/applications", tags=["applications"]
        )
        app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
        app.include_router(
            cover_letters_router, prefix="/api/v1/cover-letters", tags=["cover-letters"]
        )
        app.include_router(
            job_applications_router,
            prefix="/api/v1/job-applications",
            tags=["job-applications"],
        )
        app.include_router(
            monitoring_router, prefix="/api/v1/monitoring", tags=["monitoring"]
        )
        app.include_router(exports_router, prefix="/api/v1/exports", tags=["exports"])
        app.include_router(files_router, prefix="/api/v1/files", tags=["files"])
        app.include_router(
            config_router, prefix="/api/v1/config", tags=["configuration"]
        )
        app.include_router(cache_router, prefix="/api/v1", tags=["cache"])
        app.include_router(analytics_router, prefix="/api/v1", tags=["analytics"])
        app.include_router(
            ai_config_router, prefix="/api/v1/ai-config", tags=["ai-configuration"]
        )
        app.include_router(
            automation_router, prefix="/api/v1/automation", tags=["automation"]
        )
        app.include_router(
            scheduler_router, prefix="/api/v1/scheduler", tags=["scheduler"]
        )
        app.include_router(
            resume_builder_router, prefix="/api/v1", tags=["resume-builder"]
        )

        logger.info("All API routers loaded successfully")
    except ImportError as e:
        logger.warning(f"Some API routers could not be loaded: {e}")
        logger.info("Running with basic endpoints only")

    # Root endpoint
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Serve the main HTML interface."""
        return get_main_html()

    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        try:
            # Get detailed health if services are initialized
            if service_registry._initialized:
                health_status = await service_registry.health_check()
                return {
                    "status": "healthy",
                    "version": "1.0.0",
                    "environment": config.ENVIRONMENT,
                    "services": health_status.get("services", {}),
                }
        except Exception as e:
            logger.warning(f"Error getting detailed health: {e}")

        return {
            "status": "healthy",
            "version": "1.0.0",
            "environment": config.ENVIRONMENT,
        }

    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize the application on startup."""
        try:
            logger.info("🚀 Starting AI Job Application Assistant...")

            # Load configurations from database (if available)
            try:
                from src.config import config

                await config.load_from_database()
                logger.info("✅ Configuration loaded from database")
            except Exception as e:
                logger.warning(
                    f"Could not load configs from database: {e}. Using environment variables."
                )

            # Configuration is automatically validated by Pydantic
            logger.debug("Configuration loaded successfully")

            # Initialize services
            logger.info("Initializing services...")
            await initialize_services()
            logger.info("✅ Services initialized")

            # Start scheduler service if enabled
            try:
                scheduler_service = service_registry.get_scheduler_service()
                if scheduler_service:
                    from src.config import config

                    if getattr(config, "SCHEDULER_ENABLED", True):
                        await scheduler_service.start()
                        logger.info("✅ Scheduler service started")
                    else:
                        logger.info("Scheduler service disabled by configuration")
            except (KeyError, AttributeError) as e:
                logger.debug(f"Scheduler service not available: {e}")

            # Setup query performance monitoring (optional - don't fail if it doesn't work)
            if database_config.engine:
                try:
                    # Get monitoring service for query tracking (if available)
                    try:
                        monitoring_service = (
                            service_registry.get_monitoring_service_sync()
                        )
                        setup_query_performance_monitoring(
                            database_config.engine, monitoring_service
                        )
                    except (KeyError, AttributeError) as e:
                        logger.warning(
                            f"Monitoring service not available for query performance: {e}"
                        )
                        # Continue without monitoring service
                        setup_query_performance_monitoring(database_config.engine)
                except Exception as e:
                    logger.debug(f"Query performance monitoring not available: {e}")
                    # Don't fail startup if monitoring setup fails

            # Add metrics middleware (optional - don't fail if it doesn't work)
            try:
                from src.middleware.metrics_middleware import MetricsMiddleware

                try:
                    monitoring_service = service_registry.get_monitoring_service_sync()
                    app.add_middleware(
                        MetricsMiddleware, monitoring_service=monitoring_service
                    )
                    logger.debug("Metrics middleware added")
                except (KeyError, AttributeError) as e:
                    logger.debug(f"Metrics middleware not available: {e}")
                    # Continue without metrics middleware
            except Exception as e:
                logger.debug(f"Metrics middleware setup skipped: {e}")
                # Don't fail startup if middleware setup fails

            # Start background tasks for metrics aggregation and cleanup
            try:
                import asyncio

                monitoring_service = service_registry.get_monitoring_service_sync()
                asyncio.create_task(metrics_aggregation_task(monitoring_service))
                asyncio.create_task(metrics_cleanup_task(monitoring_service))
                logger.debug("Background tasks started")
            except Exception as e:
                logger.debug(f"Background tasks not available: {e}")

            logger.info("=" * 60)
            logger.info("✅ AI Job Application Assistant ready!")
            logger.info(f"📚 API Docs: http://localhost:{config.port}/docs")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"❌ Error during startup: {e}", exc_info=True)
            raise

    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup the application on shutdown."""
        try:
            logger.info("🔄 Shutting down AI Job Application Assistant...")

            # Stop scheduler service gracefully
            try:
                scheduler_service = service_registry.get_scheduler_service()
                if scheduler_service:
                    await scheduler_service.stop()
                    logger.info("✅ Scheduler service stopped")
            except (KeyError, AttributeError) as e:
                logger.debug(f"Scheduler service not available for shutdown: {e}")

            # Shutdown service registry
            await service_registry.shutdown()
            logger.info("✅ Services shut down")

            logger.info("👋 AI Job Application Assistant shut down complete")
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}", exc_info=True)

    return app


async def initialize_services() -> None:
    """Initialize all application services."""
    try:
        # Initialize database first (required by many services)
        if not database_config._initialized:
            logger.info("Initializing database...")
            await database_config.initialize()
            await database_config.create_tables()
            logger.info("✅ Database initialized")

        # Initialize unified service registry
        await service_registry.initialize()

        # Perform health check on all services
        health_status = await service_registry.health_check()
        logger.debug(f"Services health: {health_status}")

        # Log service availability
        ai_service = await service_registry.get_ai_service()
        ai_available = await ai_service.is_available()

        if ai_available:
            logger.debug("AI Service available")
        else:
            logger.warning("⚠️  AI Service not available - using mock responses")

    except Exception as e:
        logger.error(f"Error initializing services: {e}", exc_info=True)
        # Don't raise the exception - allow the app to start with degraded functionality
        logger.warning(
            "Some services may not be available - continuing with reduced functionality"
        )


async def metrics_aggregation_task(monitoring_service):
    """Background task for metrics aggregation."""
    import asyncio
    from src.services.monitoring_service import DatabaseMonitoringService

    if not isinstance(monitoring_service, DatabaseMonitoringService):
        return

    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            logger.info("Running hourly metrics aggregation...")
            await monitoring_service.aggregate_metrics("hourly")

            # Run daily aggregation at midnight
            from datetime import datetime

            now = datetime.now()
            if now.hour == 0 and now.minute < 5:
                logger.info("Running daily metrics aggregation...")
                await monitoring_service.aggregate_metrics("daily")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in metrics aggregation task: {e}", exc_info=True)
            await asyncio.sleep(60)  # Wait before retrying


async def metrics_cleanup_task(monitoring_service):
    """Background task for metrics cleanup."""
    import asyncio
    from src.services.monitoring_service import DatabaseMonitoringService

    if not isinstance(monitoring_service, DatabaseMonitoringService):
        return

    while True:
        try:
            await asyncio.sleep(86400)  # Run daily
            logger.info("Running metrics cleanup...")
            deleted_count = await monitoring_service.cleanup_old_metrics(
                retention_days=7
            )
            logger.info(f"Cleaned up {deleted_count} old metrics")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in metrics cleanup task: {e}", exc_info=True)
            await asyncio.sleep(3600)  # Wait before retrying


def get_main_html() -> str:
    """Get the main HTML interface."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Job Application Assistant</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }
            .header p {
                margin: 10px 0 0 0;
                font-size: 1.2em;
                opacity: 0.9;
            }
            .content {
                padding: 40px;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin: 40px 0;
            }
            .feature {
                background: #f8f9fa;
                padding: 30px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .feature h3 {
                color: #667eea;
                margin-top: 0;
            }
            .api-section {
                background: #f8f9fa;
                padding: 30px;
                border-radius: 10px;
                margin: 30px 0;
            }
            .api-section h3 {
                color: #667eea;
                margin-top: 0;
            }
            .endpoint {
                background: white;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
                border-left: 3px solid #28a745;
            }
            .endpoint code {
                background: #e9ecef;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .footer {
                text-align: center;
                padding: 20px;
                background: #f8f9fa;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI Job Application Assistant</h1>
                <p>Intelligent job searching, resume optimization, and application management</p>
            </div>
            
            <div class="content">
                <h2>🚀 Features</h2>
                <div class="features">
                    <div class="feature">
                        <h3>🔍 Smart Job Search</h3>
                        <p>Search across multiple job portals with AI-powered filtering and ranking</p>
                    </div>
                    <div class="feature">
                        <h3>📝 Resume Optimization</h3>
                        <p>Get AI suggestions to optimize your resume for specific job postings</p>
                    </div>
                    <div class="feature">
                        <h3>✉️ Cover Letter Generation</h3>
                        <p>Generate personalized cover letters using AI analysis</p>
                    </div>
                    <div class="feature">
                        <h3>📊 Application Tracking</h3>
                        <p>Track your job applications and monitor their progress</p>
                    </div>
                </div>
                
                <div class="api-section">
                    <h3>🔌 API Endpoints</h3>
                    <p>Use our RESTful API to integrate with your applications:</p>
                    
                    <div class="endpoint">
                        <strong>POST /api/v1/jobs/search</strong> - Search for jobs
                    </div>
                    <div class="endpoint">
                        <strong>POST /api/v1/ai/optimize-resume</strong> - Optimize resume
                    </div>
                    <div class="endpoint">
                        <strong>POST /api/v1/ai/generate-cover-letter</strong> - Generate cover letter
                    </div>
                    <div class="endpoint">
                        <strong>GET /api/v1/applications</strong> - Get applications
                    </div>
                    
                    <p style="margin-top: 20px;">
                        <a href="/docs" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            📚 View API Documentation
                        </a>
                    </p>
                </div>
                
                <div class="api-section">
                    <h3>⚙️ Configuration</h3>
                    <p>Make sure you have configured your Gemini API key in the <code>.env</code> file:</p>
                    <code>GEMINI_API_KEY=your_api_key_here</code>
                </div>
            </div>
            
            <div class="footer">
                <p>Built with FastAPI, Python, and Google Gemini AI</p>
            </div>
        </div>
    </body>
    </html>
    """


# Create the app instance
app = create_app()
