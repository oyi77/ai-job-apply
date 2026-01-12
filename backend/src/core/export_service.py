"""Export service interface for generating reports in various formats."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime


class ExportService(ABC):
    """Abstract interface for export services."""
    
    @abstractmethod
    async def export_applications(
        self,
        applications: List[Dict[str, Any]],
        format: str = "csv",
        user_id: Optional[str] = None
    ) -> bytes:
        """
        Export job applications in the specified format.
        
        Args:
            applications: List of application dictionaries
            format: Export format (pdf, csv, excel)
            user_id: Optional user ID for filtering
            
        Returns:
            Bytes of the exported file
        """
        pass
    
    @abstractmethod
    async def export_resumes(
        self,
        resumes: List[Dict[str, Any]],
        format: str = "csv",
        user_id: Optional[str] = None
    ) -> bytes:
        """
        Export resumes in the specified format.
        
        Args:
            resumes: List of resume dictionaries
            format: Export format (pdf, csv, excel)
            user_id: Optional user ID for filtering
            
        Returns:
            Bytes of the exported file
        """
        pass
    
    @abstractmethod
    async def export_cover_letters(
        self,
        cover_letters: List[Dict[str, Any]],
        format: str = "pdf",
        user_id: Optional[str] = None
    ) -> bytes:
        """
        Export cover letters in the specified format.
        
        Args:
            cover_letters: List of cover letter dictionaries
            format: Export format (pdf, csv, excel)
            user_id: Optional user ID for filtering
            
        Returns:
            Bytes of the exported file
        """
        pass
    
    @abstractmethod
    async def export_analytics(
        self,
        analytics_data: Dict[str, Any],
        format: str = "pdf",
        user_id: Optional[str] = None
    ) -> bytes:
        """
        Export analytics data in the specified format.
        
        Args:
            analytics_data: Dictionary containing analytics data
            format: Export format (pdf, csv, excel)
            user_id: Optional user ID for filtering
            
        Returns:
            Bytes of the exported file
        """
        pass
    
    @abstractmethod
    async def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats."""
        pass
