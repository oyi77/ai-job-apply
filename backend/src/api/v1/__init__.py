"""API v1 package for the AI Job Application Assistant."""

from .jobs import router as jobs_router
from .resumes import router as resumes_router
from .applications import router as applications_router
from .ai import router as ai_router
from .cover_letters import router as cover_letters_router

__all__ = [
    "jobs_router",
    "resumes_router", 
    "applications_router",
    "ai_router",
    "cover_letters_router",
]
