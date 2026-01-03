"""Data models for the AI Job Application Assistant."""

from src.models.job import Job, JobSearchRequest, JobSearchResponse
from src.models.application import JobApplication, ApplicationStatus
from src.models.resume import Resume, ResumeOptimizationRequest
from src.models.cover_letter import CoverLetter, CoverLetterRequest

__all__ = [
    "Job",
    "JobSearchRequest", 
    "JobSearchResponse",
    "JobApplication",
    "ApplicationStatus",
    "Resume",
    "ResumeOptimizationRequest",
    "CoverLetter",
    "CoverLetterRequest",
    "PasswordHistory",
]
