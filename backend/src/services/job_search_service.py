"""Unified job search service implementation for the AI Job Application Assistant."""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ..core.job_search import JobSearchService
from ..models.job import Job, JobSearchRequest, JobSearchResponse


class JobSearchService(JobSearchService):
    """Unified job search service with multiple platform support and fallbacks."""
    
    def __init__(self):
        """Initialize the unified job search service."""
        self.logger = logger.bind(module="JobSearchService")
        self._initialized = False
        self._jobspy_available = False
        
        # Map our experience levels to platform parameters
        self.experience_mapping = {
            "entry": "entry-level",
            "mid": "mid-level", 
            "senior": "senior-level",
            "lead": "lead-level",
            "executive": "executive-level"
        }
        
        # Supported platforms
        self.supported_platforms = [
            "indeed", "linkedin", "glassdoor", "google", 
            "zip_recruiter"
        ]
    
    async def initialize(self) -> None:
        """Initialize the service."""
        try:
            # Try to import jobspy
            try:
                import jobspy
                self._jobspy_available = True
                self.logger.info("JobSpy available for job search")
            except ImportError:
                self.logger.warning("JobSpy not available, using fallback job search")
                self._jobspy_available = False
            
            self._initialized = True
            self.logger.info("Job search service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing job search service: {e}", exc_info=True)
            self._initialized = False
    
    async def close(self) -> None:
        """Close the service and cleanup resources."""
        self._initialized = False
        self.logger.info("Job search service closed")
    
    async def search_jobs(self, request: JobSearchRequest) -> JobSearchResponse:
        """
        Search for jobs using available platforms.
        
        Args:
            request: Job search request parameters
            
        Returns:
            Job search results grouped by platform
        """
        try:
            await self.initialize()
            
            self.logger.info(f"Job search: {request.keywords} in {request.location}")
            
            if self._jobspy_available:
                return await self._search_with_jobspy(request)
            else:
                return await self._search_with_fallback(request)
                
        except Exception as e:
            self.logger.error(f"Error in job search: {e}", exc_info=True)
            raise
    
    async def _search_with_jobspy(self, request: JobSearchRequest) -> JobSearchResponse:
        """Search using JobSpy library."""
        try:
            from jobspy import scrape_jobs
            
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
                    "timestamp": datetime.utcnow(),
                    "method": "jobspy"
                }
            )
            
            self.logger.info(f"JobSpy found {response.total_jobs} jobs across {len(jobs_by_platform)} platforms")
            return response
            
        except Exception as e:
            self.logger.error(f"JobSpy search failed: {e}", exc_info=True)
            # Fallback to mock search
            return await self._search_with_fallback(request)
    
    async def _search_with_fallback(self, request: JobSearchRequest) -> JobSearchResponse:
        """Search using fallback/mock data."""
        try:
            self.logger.info("Using fallback job search")
            
            # Generate mock jobs for demonstration
            mock_jobs = self._generate_mock_jobs(request)
            
            # Group by platform
            jobs_by_platform = {
                "indeed": mock_jobs[:3],
                "linkedin": mock_jobs[3:6],
                "glassdoor": mock_jobs[6:9],
                "google": mock_jobs[9:12],
                "zip_recruiter": mock_jobs[12:15]
            }
            
            # Remove empty platforms
            jobs_by_platform = {k: v for k, v in jobs_by_platform.items() if v}
            
            response = JobSearchResponse(
                jobs=jobs_by_platform,
                total_jobs=sum(len(jobs) for jobs in jobs_by_platform.values()),
                search_metadata={
                    "keywords": request.keywords,
                    "location": request.location,
                    "experience_level": request.experience_level,
                    "sites_searched": list(jobs_by_platform.keys()),
                    "timestamp": datetime.utcnow(),
                    "method": "fallback"
                }
            )
            
            self.logger.info(f"Fallback search found {response.total_jobs} jobs")
            return response
            
        except Exception as e:
            self.logger.error(f"Fallback search failed: {e}", exc_info=True)
            raise
    
    async def search_specific_site(self, site: str, request: JobSearchRequest) -> List[Job]:
        """
        Search for jobs on a specific site.
        
        Args:
            site: Site to search on
            request: Job search request parameters
            
        Returns:
            List of jobs found on the specific site
        """
        try:
            if site not in self.supported_platforms:
                self.logger.warning(f"Unsupported site: {site}")
                return []
            
            await self.initialize()
            
            if self._jobspy_available:
                return await self._search_specific_site_with_jobspy(site, request)
            else:
                return await self._search_specific_site_fallback(site, request)
            
        except Exception as e:
            self.logger.error(f"Error searching specific site {site}: {e}")
            return []
    
    async def _search_specific_site_with_jobspy(self, site: str, request: JobSearchRequest) -> List[Job]:
        """Search specific site using JobSpy."""
        try:
            from jobspy import scrape_jobs
            
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
            self.logger.error(f"JobSpy search for {site} failed: {e}")
            return []
    
    async def _search_specific_site_fallback(self, site: str, request: JobSearchRequest) -> List[Job]:
        """Search specific site using fallback."""
        try:
            # Generate mock jobs for the specific site
            mock_jobs = self._generate_mock_jobs(request)
            
            # Return a subset for the specific site
            site_jobs = mock_jobs[:3]  # 3 jobs per site
            
            self.logger.info(f"Fallback search for {site} found {len(site_jobs)} jobs")
            return site_jobs
            
        except Exception as e:
            self.logger.error(f"Fallback search for {site} failed: {e}")
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
            
            # For now, return a mock job with the given ID
            # In a real implementation, this would fetch from the platform
            mock_job = Job(
                title=f"Mock Job {job_id}",
                company="Mock Company",
                location="Mock Location",
                url=f"https://{platform}.com/job/{job_id}",
                portal=platform,
                description="This is a mock job description for demonstration purposes.",
                salary="Not specified",
                posted_date="Recently",
                experience_level="mid",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.logger.info(f"Retrieved mock job details for {job_id} on {platform}")
            return mock_job
            
        except Exception as e:
            self.logger.error(f"Error getting job details: {e}")
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
                self.logger.info("No jobs found from JobSpy")
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
                        self.logger.debug(f"Error converting job from {platform}: {e}")
                        continue
                
                if platform_jobs:
                    jobs_by_platform[platform] = platform_jobs
                    self.logger.debug(f"Converted {len(platform_jobs)} jobs from {platform}")
            
        except Exception as e:
            self.logger.error(f"Error converting JobSpy results: {e}")
        
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
            if hasattr(row, 'min_amount') and hasattr(row, 'max_amount'):
                min_amount = getattr(row, 'min_amount', None)
                max_amount = getattr(row, 'max_amount', None)
                if min_amount and max_amount:
                    salary = f"${min_amount:,} - ${max_amount:,}"
                elif min_amount:
                    salary = f"${min_amount:,}+"
            
            # Extract job type
            job_type = str(getattr(row, 'job_type', 'Not specified'))
            
            # Extract posted date
            posted_date = "Recently"
            if hasattr(row, 'date_posted'):
                posted_date = str(getattr(row, 'date_posted', 'Recently'))
            
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
            self.logger.debug(f"Error converting job row: {e}")
            return None
    
    def _generate_mock_jobs(self, request: JobSearchRequest) -> List[Job]:
        """Generate mock jobs for fallback search."""
        mock_jobs = []
        
        # Sample job titles based on keywords
        sample_titles = [
            "Senior Software Engineer",
            "Full Stack Developer", 
            "Python Developer",
            "React Developer",
            "DevOps Engineer",
            "Data Scientist",
            "Product Manager",
            "UX Designer",
            "QA Engineer",
            "System Administrator",
            "Cloud Engineer",
            "Machine Learning Engineer",
            "Frontend Developer",
            "Backend Developer",
            "Mobile Developer"
        ]
        
        # Sample companies
        sample_companies = [
            "TechCorp Inc.",
            "Innovation Labs",
            "StartupXYZ",
            "BigTech Company",
            "Digital Solutions",
            "Cloud Systems",
            "Data Analytics Corp",
            "AI Innovations",
            "Web Solutions",
            "Mobile Apps Inc.",
            "Enterprise Software",
            "Startup Hub",
            "Tech Startup",
            "Digital Agency",
            "Software Corp"
        ]
        
        # Generate mock jobs
        for i in range(15):
            job = Job(
                title=sample_titles[i % len(sample_titles)],
                company=sample_companies[i % len(sample_companies)],
                location=request.location,
                url=f"https://example.com/job/{i+1}",
                portal="mock",
                description=f"This is a mock job description for {sample_titles[i % len(sample_titles)]} position. This job requires experience in the technologies mentioned in your search.",
                salary="$80,000 - $120,000",
                posted_date="Recently",
                experience_level=request.experience_level or "mid",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            mock_jobs.append(job)
        
        return mock_jobs
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        try:
            return {
                "status": "healthy",
                "available": self._initialized,
                "jobspy_available": self._jobspy_available,
                "supported_platforms": len(self.supported_platforms)
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "available": False,
                "error": str(e)
            }
