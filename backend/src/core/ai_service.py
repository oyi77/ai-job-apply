"""AI service interface for job application assistance."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..models.resume import ResumeOptimizationRequest, ResumeOptimizationResponse
from ..models.cover_letter import CoverLetterRequest, CoverLetter


class AIService(ABC):
    """Abstract interface for AI-powered services."""
    
    @abstractmethod
    async def optimize_resume(self, request: ResumeOptimizationRequest) -> ResumeOptimizationResponse:
        """Optimize resume for a specific job."""
        pass
    
    @abstractmethod
    async def generate_cover_letter(self, request: CoverLetterRequest) -> CoverLetter:
        """Generate a personalized cover letter."""
        pass
    
    @abstractmethod
    async def analyze_job_match(self, resume_content: str, job_description: str) -> Dict[str, Any]:
        """Analyze how well a resume matches a job description."""
        pass
    
    @abstractmethod
    async def extract_resume_skills(self, resume_content: str) -> List[str]:
        """Extract skills from resume content."""
        pass
    
    @abstractmethod
    async def suggest_resume_improvements(self, resume_content: str, job_description: str) -> List[str]:
        """Suggest improvements for a resume based on job description."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the AI service is available."""
        pass
    
    @abstractmethod
    async def prepare_interview(self, job_description: str, resume_content: str, company_name: Optional[str] = None, job_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare interview questions and tips based on job description and resume.
        
        Args:
            job_description: Full job description text
            resume_content: Resume content text
            company_name: Optional company name
            job_title: Optional job title
            
        Returns:
            Dictionary with interview questions, answers, tips, and preparation guidance
        """
        pass