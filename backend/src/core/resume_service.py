"""Resume service interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.resume import Resume


class ResumeService(ABC):
    """Abstract interface for resume management services."""
    
    @abstractmethod
    async def upload_resume(self, file_path: str, name: str) -> Resume:
        """Upload and process a new resume."""
        pass
    
    @abstractmethod
    async def get_resume(self, resume_id: str) -> Optional[Resume]:
        """Get a resume by ID."""
        pass
    
    @abstractmethod
    async def get_all_resumes(self) -> List[Resume]:
        """Get all available resumes."""
        pass
    
    @abstractmethod
    async def get_default_resume(self) -> Optional[Resume]:
        """Get the default resume."""
        pass
    
    @abstractmethod
    async def set_default_resume(self, resume_id: str) -> bool:
        """Set a resume as the default."""
        pass
    
    @abstractmethod
    async def delete_resume(self, resume_id: str) -> bool:
        """Delete a resume."""
        pass
    
    @abstractmethod
    async def extract_text(self, resume: Resume) -> str:
        """Extract text content from resume file."""
        pass
    
    @abstractmethod
    async def update_resume(self, resume_id: str, updates: dict) -> Optional[Resume]:
        """Update resume information."""
        pass
