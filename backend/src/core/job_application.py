"""Abstract base class for job application service."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from src.models.job import Job, ApplicationInfo, ApplicationForm
from src.models.resume import Resume


class JobApplicationService(ABC):
    """Abstract base class for job application service."""
    
    @abstractmethod
    async def get_application_info(self, job: Job) -> ApplicationInfo:
        """
        Extract application information from a job posting.
        
        Args:
            job: Job posting to extract application info from
            
        Returns:
            Application information including method, URLs, and forms
        """
        pass
    
    @abstractmethod
    async def apply_to_job(self, job: Job, resume: Resume, cover_letter: str, 
                          additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Apply to a job using the appropriate method.
        
        Args:
            job: Job to apply to
            resume: Resume to submit
            cover_letter: Cover letter text
            additional_data: Additional form data or preferences
            
        Returns:
            Application result with status and details
        """
        pass
    
    @abstractmethod
    async def get_application_status(self, application_id: str) -> Dict[str, Any]:
        """
        Check the status of a submitted application.
        
        Args:
            application_id: Unique identifier for the application
            
        Returns:
            Application status information
        """
        pass
    
    @abstractmethod
    async def extract_application_form(self, job_url: str) -> Optional[ApplicationForm]:
        """
        Extract application form information from a job posting page.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Application form information if available
        """
        pass
    
    @abstractmethod
    async def validate_application_data(self, job: Job, resume: Resume, 
                                     cover_letter: str) -> Dict[str, Any]:
        """
        Validate application data before submission.
        
        Args:
            job: Job to apply to
            resume: Resume to submit
            cover_letter: Cover letter text
            
        Returns:
            Validation results with any errors or warnings
        """
        pass
    
    @abstractmethod
    async def get_supported_platforms(self) -> List[str]:
        """
        Get list of platforms that support automated applications.
        
        Returns:
            List of supported platform names
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health and availability.
        
        Returns:
            Health status information
        """
        pass
