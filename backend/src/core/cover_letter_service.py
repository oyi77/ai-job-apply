"""Cover letter service interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..models.cover_letter import CoverLetter, CoverLetterCreate, CoverLetterUpdate


class CoverLetterService(ABC):
    """Abstract base class for cover letter services."""
    
    @abstractmethod
    async def get_all_cover_letters(self) -> List[CoverLetter]:
        """Get all cover letters."""
        pass
    
    @abstractmethod
    async def get_cover_letter(self, cover_letter_id: str) -> Optional[CoverLetter]:
        """Get a specific cover letter by ID."""
        pass
    
    @abstractmethod
    async def create_cover_letter(self, cover_letter_data: CoverLetterCreate) -> CoverLetter:
        """Create a new cover letter."""
        pass
    
    @abstractmethod
    async def update_cover_letter(self, cover_letter_id: str, updates: CoverLetterUpdate) -> Optional[CoverLetter]:
        """Update an existing cover letter."""
        pass
    
    @abstractmethod
    async def delete_cover_letter(self, cover_letter_id: str) -> bool:
        """Delete a cover letter."""
        pass
    
    @abstractmethod
    async def generate_cover_letter(self, job_title: str, company_name: str, job_description: str, resume_summary: str, tone: str = "professional") -> CoverLetter:
        """Generate a cover letter using AI."""
        pass
