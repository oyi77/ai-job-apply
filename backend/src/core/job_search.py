"""Job search service interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.models.job import JobSearchRequest, JobSearchResponse, Job


class JobSearchService(ABC):
    """Abstract interface for job search services."""
    
    @abstractmethod
    async def search_jobs(self, request: JobSearchRequest) -> JobSearchResponse:
        """Search for jobs based on the request."""
        pass
    
    @abstractmethod
    async def search_specific_site(self, site: str, request: JobSearchRequest) -> List[Job]:
        """Search for jobs on a specific site."""
        pass
    
    @abstractmethod
    async def get_job_details(self, job_url: str, portal: str) -> Optional[Job]:
        """Get detailed job information from a specific URL."""
        pass
    
    @abstractmethod
    def get_available_sites(self) -> List[str]:
        """Get list of available job search sites."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the service is available and working."""
        pass
