"""JobSpy-based job search service implementation."""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from jobspy import scrape_jobs
from ..core.job_search import JobSearchService
from ..models.job import Job, JobSearchRequest, JobSearchResponse
from ..utils.logger import get_logger
import pandas as pd

logger = get_logger(__name__)


class JobSpyJobService(JobSearchService):
    """JobSpy-based job search service implementation."""
    
    def __init__(self):
        """Initialize the JobSpy job search service."""
        self.logger = get_logger(__name__)
        self._initialized = False
        
        # Map our experience levels to JobSpy parameters
        self.experience_mapping = {
            "entry": "entry-level",
            "mid": "mid-level", 
            "senior": "senior-level",
            "lead": "lead-level",
            "executive": "executive-level"
        }
        
        # Supported platforms (focus on the most reliable ones)
        self.supported_platforms = [
            "indeed", "linkedin", "glassdoor", "google", 
            "zip_recruiter"
        ]
    
    async def initialize(self) -> None:
        """Initialize the service."""
        self._initialized = True
        logger.info("JobSpy job search service initialized")
    
    async def close(self) -> None:
        """Close the service and cleanup resources."""
        self._initialized = False
        logger.info("JobSpy job search service closed")
    
    async def search_jobs(self, request: JobSearchRequest) -> JobSearchResponse:
        """
        Search for jobs using JobSpy.
        
        Args:
            request: Job search request parameters
            
        Returns:
            Job search results grouped by platform
        """
        try:
            await self.initialize()
            
            logger.info(f"JobSpy search: {request.keywords} in {request.location}")
            
            # Convert our request to JobSpy parameters
            jobspy_params = self._build_jobspy_params(request)
            
            # Run JobSpy search in executor to avoid blocking
            loop = asyncio.get_event_loop()
            jobs_df = await loop.run_in_executor(
                None, 
                lambda: scrape_jobs(**jobspy_params)
            )
            
            # Convert JobSpy results to our format
            jobs_by_platform = self._convert_jobspy_results(jobs_df, request)
            
            # Create response
            response = JobSearchResponse(
                jobs=jobs_by_platform,
                total_jobs=sum(len(jobs) for jobs in jobs_by_platform.values()),
                search_metadata={
                    "keywords": request.keywords,
                    "location": request.location,
                    "experience_level": request.experience_level,
                    "sites_searched": list(jobs_by_platform.keys()),
                    "timestamp": datetime.utcnow()
                }
            )
            
            logger.info(f"JobSpy found {response.total_jobs} jobs across {len(jobs_by_platform)} platforms")
            return response
            
        except Exception as e:
            logger.error(f"Error in JobSpy job search: {e}", exc_info=True)
            raise
    
    async def search_specific_site(self, site: str, request: JobSearchRequest) -> List[Job]:
        """
        Search for jobs on a specific site using JobSpy.
        
        Args:
            site: Site to search on
            request: Job search request parameters
            
        Returns:
            List of jobs found on the specific site
        """
        try:
            if site not in self.supported_platforms:
                logger.warning(f"Unsupported site: {site}")
                return []
            
            await self.initialize()
            
            # Build parameters for single site search
            jobspy_params = self._build_jobspy_params(request)
            jobspy_params["site_name"] = [site]
            
            # Run JobSpy search
            loop = asyncio.get_event_loop()
            jobs_df = await loop.run_in_executor(
                None, 
                lambda: scrape_jobs(**jobspy_params)
            )
            
            # Convert results
            jobs_by_platform = self._convert_jobspy_results(jobs_df, request)
            return jobs_by_platform.get(site, [])
            
        except Exception as e:
            logger.error(f"Error searching specific site {site}: {e}")
            return []
    
    async def get_job_details(self, job_id: str, platform: str) -> Optional[Job]:
        """
        Get detailed job information by ID and platform.
        
        Args:
            job_id: Job identifier
            platform: Platform name
            
        Returns:
            Detailed job information or None if not found
        """
        try:
            await self.initialize()
            
            # JobSpy doesn't support getting individual job details by ID
            # This would require platform-specific implementation
            logger.info(f"Job details not yet implemented for {platform}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return None
    
    def get_available_sites(self) -> List[str]:
        """Get list of available job search sites."""
        return self.supported_platforms.copy()
    
    async def is_available(self) -> bool:
        """Check if the service is available."""
        return self._initialized
    
    def _build_jobspy_params(self, request: JobSearchRequest) -> Dict[str, Any]:
        """Build JobSpy parameters from our request."""
        params = {
            "site_name": self.supported_platforms,  # Search all supported platforms
            "search_term": " ".join(request.keywords),
            "location": request.location,
            "results_wanted": 10,  # Conservative limit per platform
            "country_indeed": "USA",  # Default to USA
        }
        
        # Add experience level filtering if specified
        if request.experience_level and request.experience_level in self.experience_mapping:
            # Note: JobSpy doesn't directly support experience level filtering
            # We could enhance the search terms to include experience level
            enhanced_keywords = request.keywords + [self.experience_mapping[request.experience_level]]
            params["search_term"] = " ".join(enhanced_keywords)
        
        # Add job type filtering if specified
        if hasattr(request, 'job_type') and request.job_type:
            params["job_type"] = request.job_type
        
        # Add remote work filtering if specified
        if hasattr(request, 'is_remote') and request.is_remote:
            params["is_remote"] = request.is_remote
        
        return params
    
    def _convert_jobspy_results(self, jobs_df, request: JobSearchRequest) -> Dict[str, List[Job]]:
        """Convert JobSpy DataFrame results to our format."""
        jobs_by_platform = {}
        
        try:
            if jobs_df.empty:
                logger.info("No jobs found from JobSpy")
                return jobs_by_platform
            
            # Group jobs by platform
            for platform in self.supported_platforms:
                platform_jobs = []
                
                # Filter jobs for this platform
                platform_df = jobs_df[jobs_df['site'] == platform]
                
                for _, row in platform_df.iterrows():
                    try:
                        # Convert JobSpy row to our Job model
                        job = self._convert_jobspy_row(row, platform, request)
                        if job:
                            platform_jobs.append(job)
                    except Exception as e:
                        logger.debug(f"Error converting job from {platform}: {e}")
                        continue
                
                if platform_jobs:
                    jobs_by_platform[platform] = platform_jobs
                    logger.debug(f"Converted {len(platform_jobs)} jobs from {platform}")
            
        except Exception as e:
            logger.error(f"Error converting JobSpy results: {e}")
        
        return jobs_by_platform
    
    def _convert_jobspy_row(self, row, platform: str, request: JobSearchRequest) -> Optional[Job]:
        """Convert a single JobSpy row to our Job model."""
        try:
            # Extract basic information using correct column names
            title = str(row.get('title', 'Unknown Position'))
            company = str(row.get('company', 'Unknown Company'))
            
            # Handle location - JobSpy has a single location column
            location = str(row.get('location', request.location))
            
            job_url = str(row.get('job_url', ''))
            description = str(row.get('description', ''))
            
            # Extract salary information
            salary = "Not specified"
            if pd.notna(row.get('min_amount')) and pd.notna(row.get('max_amount')):
                min_amount = row.get('min_amount')
                max_amount = row.get('max_amount')
                if min_amount and max_amount:
                    salary = f"${min_amount:,} - ${max_amount:,}"
            elif pd.notna(row.get('min_amount')):
                salary = f"${row.get('min_amount'):,}+"
            
            # Extract job type
            job_type = str(row.get('job_type', 'Not specified'))
            
            # Extract posted date
            posted_date = "Recently"
            if pd.notna(row.get('date_posted')):
                posted_date = str(row.get('date_posted'))
            
            # Create Job object
            job = Job(
                title=title,
                company=company,
                location=location,
                url=job_url,
                portal=platform,
                description=description[:500] + "..." if len(description) > 500 else description,
                salary=salary,
                posted_date=posted_date,
                experience_level=request.experience_level,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return job
            
        except Exception as e:
            logger.debug(f"Error converting job row: {e}")
            return None
