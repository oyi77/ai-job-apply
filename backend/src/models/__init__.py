"""Data models for the AI Job Application Assistant."""

from .job import Job, JobSearchRequest, JobSearchResponse
from .application import JobApplication, ApplicationStatus
from .resume import Resume, ResumeOptimizationRequest
from .cover_letter import CoverLetter, CoverLetterRequest

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
]
