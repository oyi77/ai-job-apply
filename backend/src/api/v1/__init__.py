"""API v1 package for the AI Job Application Assistant."""

from src.api.v1.auth import router as auth_router
from src.api.v1.jobs import router as jobs_router
from src.api.v1.resumes import router as resumes_router
from src.api.v1.applications import router as applications_router
from src.api.v1.ai import router as ai_router
from src.api.v1.cover_letters import router as cover_letters_router

__all__ = [
    "auth_router",
    "jobs_router",
    "resumes_router", 
    "applications_router",
    "ai_router",
    "cover_letters_router",
]
