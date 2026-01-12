"""Application management service interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from src.models.application import JobApplication, ApplicationUpdateRequest, ApplicationStatus


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

    @abstractmethod
    async def bulk_create_applications(self, applications_data: List[Dict[str, Any]], user_id: Optional[str] = None) -> List[JobApplication]:
        """Create multiple job applications."""
        pass

    @abstractmethod
    async def bulk_update_applications(self, application_ids: List[str], updates: ApplicationUpdateRequest, user_id: Optional[str] = None) -> List[JobApplication]:
        """Update multiple job applications."""
        pass

    @abstractmethod
    async def bulk_delete_applications(self, application_ids: List[str], user_id: Optional[str] = None) -> bool:
        """Delete multiple job applications."""
        pass

    @abstractmethod
    async def export_applications(self, application_ids: Optional[List[str]] = None, format: str = "csv", user_id: Optional[str] = None) -> bytes:
        """Export applications in the specified format."""
        pass
