"""Application management service interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..models.application import JobApplication, ApplicationUpdateRequest, ApplicationStatus


class ApplicationService(ABC):
    """Abstract interface for job application management services."""
    
    @abstractmethod
    async def create_application(self, job_info: Dict[str, Any], resume_path: Optional[str] = None) -> JobApplication:
        """Create a new job application."""
        pass
    
    @abstractmethod
    async def get_application(self, application_id: str) -> Optional[JobApplication]:
        """Get an application by ID."""
        pass
    
    @abstractmethod
    async def get_all_applications(self) -> List[JobApplication]:
        """Get all applications."""
        pass
    
    @abstractmethod
    async def get_applications_by_status(self, status: ApplicationStatus) -> List[JobApplication]:
        """Get applications by status."""
        pass
    
    @abstractmethod
    async def update_application(self, application_id: str, updates: ApplicationUpdateRequest) -> Optional[JobApplication]:
        """Update application status and information."""
        pass
    
    @abstractmethod
    async def delete_application(self, application_id: str) -> bool:
        """Delete an application."""
        pass
    
    @abstractmethod
    async def get_application_stats(self) -> Dict[str, Any]:
        """Get application statistics."""
        pass
    
    @abstractmethod
    async def schedule_follow_up(self, application_id: str, follow_up_date: str) -> bool:
        """Schedule a follow-up for an application."""
        pass
    
    @abstractmethod
    async def get_upcoming_follow_ups(self) -> List[JobApplication]:
        """Get applications with upcoming follow-ups."""
        pass
