"""Unified job search service implementation for the AI Job Application Assistant."""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
import re # Added for regex operations

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
            # Try to import jobspy (check both possible package names)
            try:
                import jobspy
                self._jobspy_available = True
                self.logger.info("JobSpy available for job search")
            except ImportError:
                try:
                    import python_jobspy as jobspy
                    self._jobspy_available = True
                    self.logger.info("python-jobspy available for job search")
                except ImportError:
                    self.logger.warning(
                        "JobSpy not available (neither 'jobspy' nor 'python-jobspy' found), "
                        "using enhanced fallback job search with realistic mock data"
                    )
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
        import time
        start_time = time.time()
        
        try:
            await self.initialize()
            
            self.logger.info(
                f"Job search initiated: keywords={request.keywords}, "
                f"location={request.location}, experience={request.experience_level}"
            )
            
            if self._jobspy_available:
                try:
                    response = await self._search_with_jobspy(request)
                    elapsed_time = time.time() - start_time
                    self.logger.info(
                        f"JobSpy search completed: {response.total_jobs} jobs found "
                        f"across {len(response.jobs)} platforms in {elapsed_time:.2f}s"
                    )
                    return response
                except Exception as e:
                    self.logger.warning(
                        f"JobSpy search failed, falling back to enhanced fallback: {e}"
                    )
                    # Fall through to fallback
                    return await self._search_with_fallback(request, fallback_reason=str(e))
            else:
                return await self._search_with_fallback(request)
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(
                f"Job search failed after {elapsed_time:.2f}s: {e}",
                exc_info=True
            )
            # Return empty response with error indication instead of raising
            return JobSearchResponse(
                jobs={},
                total_jobs=0,
                search_metadata={
                    "keywords": request.keywords,
                    "location": request.location,
                    "experience_level": request.experience_level,
                    "sites_searched": [],
                    "timestamp": datetime.utcnow(),
                    "method": "fallback",
                    "error": f"Job search failed: {str(e)}",
                    "fallback_used": True
                }
            )
    
    async def _search_with_jobspy(self, request: JobSearchRequest) -> JobSearchResponse:
        """Search using JobSpy library with retry logic."""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                from jobspy import scrape_jobs
                
                # Convert our request to JobSpy parameters
                jobspy_params = self._build_jobspy_params(request)
                
                self.logger.debug(
                    f"JobSpy search attempt {attempt + 1}/{max_retries} "
                    f"with params: {jobspy_params}"
                )
                
                # Run JobSpy search in executor to avoid blocking
                loop = asyncio.get_event_loop()
                jobs_df = await loop.run_in_executor(
                    None, 
                    lambda: scrape_jobs(**jobspy_params)
                )
                
                # Convert JobSpy results to our format
                response = self._convert_jobspy_results(jobs_df, request)
                self.logger.info(
                    f"JobSpy search succeeded on attempt {attempt + 1}: "
                    f"{response.total_jobs} jobs found"
                )
                return response
                
            except ImportError as e:
                self.logger.warning(
                    f"JobSpy import failed, cannot retry: {e}"
                )
                # Cannot retry import errors
                return await self._search_with_fallback(
                    request, 
                    fallback_reason=f"JobSpy not available: {str(e)}"
                )
            except Exception as e:
                error_msg = str(e)
                is_network_error = any(
                    keyword in error_msg.lower() 
                    for keyword in ['network', 'connection', 'timeout', 'dns', 'http']
                )
                
                if attempt < max_retries - 1 and is_network_error:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(
                        f"JobSpy search failed (network error) on attempt {attempt + 1}: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    self.logger.error(
                        f"JobSpy search failed after {attempt + 1} attempts: {e}",
                        exc_info=True
                    )
                    # Fallback to mock search
                    return await self._search_with_fallback(
                        request,
                        fallback_reason=f"JobSpy search failed: {error_msg}"
                    )
        
        # Should not reach here, but just in case
        return await self._search_with_fallback(
            request,
            fallback_reason="JobSpy search failed after all retries"
        )
    
    async def _search_with_fallback(
        self, 
        request: JobSearchRequest, 
        fallback_reason: Optional[str] = None
    ) -> JobSearchResponse:
        """
        Search using enhanced fallback with realistic mock data.
        
        Args:
            request: Job search request parameters
            fallback_reason: Reason for using fallback (if any)
        """
        try:
            reason_msg = f" (reason: {fallback_reason})" if fallback_reason else ""
            self.logger.info(
                f"Using enhanced fallback job search{reason_msg}. "
                f"Generating realistic mock jobs based on search criteria."
            )
            
            # Generate realistic mock jobs based on search criteria
            mock_jobs = self._generate_mock_jobs(request)
            
            # Group by platform with better distribution
            platform_distribution = {
                "indeed": mock_jobs[:3],
                "linkedin": mock_jobs[3:6],
                "glassdoor": mock_jobs[6:9],
                "google": mock_jobs[9:12],
                "zip_recruiter": mock_jobs[12:15]
            }
            
            # Remove empty platforms
            jobs_by_platform = {
                k: v for k, v in platform_distribution.items() 
                if v and len(v) > 0
            }
            
            total_jobs = sum(len(jobs) for jobs in jobs_by_platform.values())
            
            response = JobSearchResponse(
                jobs=jobs_by_platform,
                total_jobs=total_jobs,
                search_metadata={
                    "keywords": request.keywords,
                    "location": request.location,
                    "experience_level": request.experience_level,
                    "sites_searched": list(jobs_by_platform.keys()),
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": "fallback",
                    "fallback_used": True,
                    "fallback_reason": fallback_reason or "JobSpy not available",
                    "note": "Results are generated mock data for demonstration purposes. "
                           "Install JobSpy for real job search results."
                }
            )
            
            self.logger.info(
                f"Enhanced fallback search completed: {total_jobs} jobs found "
                f"across {len(jobs_by_platform)} platforms. "
                f"Platforms: {', '.join(jobs_by_platform.keys())}"
            )
            return response
            
        except Exception as e:
            self.logger.error(
                f"Enhanced fallback search failed: {e}",
                exc_info=True
            )
            # Return empty response instead of raising to prevent complete failure
            return JobSearchResponse(
                jobs={},
                total_jobs=0,
                search_metadata={
                    "keywords": request.keywords,
                    "location": request.location,
                    "experience_level": request.experience_level,
                    "sites_searched": [],
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": "fallback",
                    "fallback_used": True,
                    "error": f"Fallback search failed: {str(e)}"
                }
            )
    
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
            return self._convert_jobspy_results(jobs_df, request)
            
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
    
    def _convert_jobspy_results(self, jobs_df, request: JobSearchRequest) -> JobSearchResponse:
        """Convert JobSpy results to our format."""
        try:
            jobs_by_platform = {}
            
            for _, row in jobs_df.iterrows():
                job = self._convert_job_row(row, request)
                if job:
                    platform = job.portal.lower()
                    if platform not in jobs_by_platform:
                        jobs_by_platform[platform] = []
                    jobs_by_platform[platform].append(job)
            
            total_jobs = sum(len(jobs) for jobs in jobs_by_platform.values())
            
            return JobSearchResponse(
                jobs=jobs_by_platform,
                total_jobs=total_jobs,
                search_metadata={
                    "keywords": request.keywords,
                    "location": request.location,
                    "experience_level": request.experience_level,
                    "sources": list(jobs_by_platform.keys())
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error converting JobSpy results: {e}", exc_info=True)
            raise
    
    def _convert_job_row(self, row, request: JobSearchRequest) -> Optional[Job]:
        """Convert a JobSpy row to our Job model."""
        try:
            # Extract basic information
            title = str(row.get('title', 'Unknown Title')).strip()
            company = str(row.get('company', 'Unknown Company')).strip()
            location = str(row.get('location', request.location)).strip()
            job_url = str(row.get('job_url', ''))
            description = str(row.get('description', ''))
            salary = str(row.get('salary', 'Not specified'))
            posted_date = str(row.get('posted_date', 'Recently'))
            
            # Determine platform from URL
            platform = "unknown"
            if "linkedin.com" in job_url.lower():
                platform = "linkedin"
            elif "indeed.com" in job_url.lower():
                platform = "indeed"
            elif "glassdoor.com" in job_url.lower():
                platform = "glassdoor"
            elif "google.com" in job_url.lower():
                platform = "google_jobs"
            elif "ziprecruiter.com" in job_url.lower():
                platform = "zip_recruiter"
            
            # Extract application information
            apply_url = self._extract_apply_url(job_url, description)
            contact_email = self._extract_contact_email(description)
            contact_phone = self._extract_contact_phone(description)
            external_application = bool(apply_url and apply_url != job_url)
            
            # Extract requirements and skills
            requirements = self._extract_requirements(description)
            skills = self._extract_skills(description)
            
            # Create Job object with enhanced application info
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
                requirements=requirements,
                skills=skills,
                # Application-related fields
                apply_url=apply_url,
                contact_email=contact_email,
                contact_phone=contact_phone,
                external_application=external_application,
                application_method=self._determine_application_method(apply_url, contact_email, platform),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return job
            
        except Exception as e:
            self.logger.debug(f"Error converting job row: {e}")
            return None
    
    def _extract_apply_url(self, job_url: str, description: str) -> Optional[str]:
        """Extract application URL from job information."""
        # Look for common apply button patterns
        apply_patterns = [
            r'apply[^"]*"([^"]*)"',
            r'application[^"]*"([^"]*)"',
            r'apply-now[^"]*"([^"]*)"',
            r'apply-button[^"]*"([^"]*)"',
            r'https?://[^\s<>"]*apply[^\s<>"]*',
            r'https?://[^\s<>"]*application[^\s<>"]*'
        ]
        
        for pattern in apply_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                url = match.group(1) if match.groups() else match.group(0)
                if url.startswith('http'):
                    return url
                elif url.startswith('/'):
                    # Relative URL, make it absolute
                    from urllib.parse import urljoin
                    return urljoin(job_url, url)
        
        return None
    
    def _extract_contact_email(self, description: str) -> Optional[str]:
        """Extract contact email from job description."""
        email_patterns = [
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'email[^:]*:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'contact[^:]*:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'send[^:]*:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        ]
        
        for pattern in email_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                email = match.group(1) if match.groups() else match.group(0)
                if '@' in email and '.' in email.split('@')[1]:
                    return email
        
        return None
    
    def _extract_contact_phone(self, description: str) -> Optional[str]:
        """Extract contact phone from job description."""
        phone_patterns = [
            r'\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}',
            r'phone[^:]*:\s*([0-9\s\(\)\-\+\.]+)',
            r'tel[^:]*:\s*([0-9\s\(\)\-\+\.]+)',
            r'call[^:]*:\s*([0-9\s\(\)\-\+\.]+)'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                phone = match.group(1) if match.groups() else match.group(0)
                # Clean up phone number
                phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone).strip()
                if len(phone) >= 10:  # Minimum valid phone length
                    return phone
        
        return None
    
    def _extract_requirements(self, description: str) -> List[str]:
        """Extract job requirements from description."""
        requirements = []
        
        # Look for requirements sections
        req_patterns = [
            r'requirements?[^:]*:\s*(.*?)(?=\n\n|\n[A-Z]|$)',
            r'qualifications?[^:]*:\s*(.*?)(?=\n\n|\n[A-Z]|$)',
            r'what you need[^:]*:\s*(.*?)(?=\n\n|\n[A-Z]|$)',
            r'you should have[^:]*:\s*(.*?)(?=\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in req_patterns:
            match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
            if match:
                req_text = match.group(1).strip()
                # Split by common list indicators
                req_items = re.split(r'[•\-\*]\s*|\d+\.\s*|\n', req_text)
                requirements.extend([item.strip() for item in req_items if item.strip() and len(item.strip()) > 10])
                break
        
        return requirements[:10]  # Limit to 10 requirements
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract required skills from description."""
        skills = []
        
        # Common technical skills
        tech_skills = [
            'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            'machine learning', 'ai', 'data science', 'statistics', 'analytics'
        ]
        
        # Look for skills in description
        for skill in tech_skills:
            if re.search(rf'\b{re.escape(skill)}\b', description, re.IGNORECASE):
                skills.append(skill.title())
        
        # Look for skill sections
        skill_patterns = [
            r'skills?[^:]*:\s*(.*?)(?=\n\n|\n[A-Z]|$)',
            r'technologies?[^:]*:\s*(.*?)(?=\n\n|\n[A-Z]|$)',
            r'tools?[^:]*:\s*(.*?)(?=\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in skill_patterns:
            match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
            if match:
                skill_text = match.group(1).strip()
                # Extract individual skills
                skill_items = re.split(r'[•\-\*]\s*|,\s*|\n', skill_text)
                skills.extend([item.strip().title() for item in skill_items if item.strip() and len(item.strip()) > 2])
                break
        
        return list(set(skills))[:15]  # Remove duplicates and limit to 15
    
    def _determine_application_method(self, apply_url: Optional[str], contact_email: Optional[str], platform: str) -> str:
        """Determine the best application method for a job."""
        if apply_url and apply_url != "unknown":
            return "direct_url"
        elif contact_email:
            return "email"
        elif platform in ["linkedin", "indeed", "glassdoor"]:
            return "form"
        else:
            return "unknown"
    
    def _generate_mock_jobs(self, request: JobSearchRequest) -> List[Job]:
        """Generate realistic mock jobs for fallback search based on search criteria."""
        mock_jobs = []
        
        # Generate job titles based on keywords and experience level
        keyword_str = " ".join(request.keywords).lower()
        experience = request.experience_level or "mid"
        
        # Base titles that match common keywords
        base_titles = []
        if any(kw in keyword_str for kw in ["python", "developer", "software", "engineer"]):
            base_titles = [
                f"{experience.title()} Python Developer",
                f"{experience.title()} Software Engineer",
                f"Full Stack {experience.title()} Developer",
                f"{experience.title()} Backend Engineer",
            ]
        elif any(kw in keyword_str for kw in ["react", "frontend", "ui", "javascript"]):
            base_titles = [
                f"{experience.title()} React Developer",
                f"{experience.title()} Frontend Engineer",
                f"{experience.title()} UI/UX Developer",
                f"Full Stack {experience.title()} Developer",
            ]
        elif any(kw in keyword_str for kw in ["data", "analyst", "scientist", "ml", "ai"]):
            base_titles = [
                f"{experience.title()} Data Scientist",
                f"{experience.title()} Data Analyst",
                f"{experience.title()} Machine Learning Engineer",
                f"{experience.title()} AI Engineer",
            ]
        else:
            # Generic titles based on experience level
            base_titles = [
                f"{experience.title()} Software Developer",
                f"{experience.title()} Engineer",
                f"{experience.title()} Developer",
                f"{experience.title()} Specialist",
            ]
        
        # Fallback to default titles if no match
        sample_titles = base_titles + [
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
        
        # Sample application methods and URLs
        application_methods = [
            ("direct_url", "https://careers.techcorp.com/apply/12345"),
            ("email", "careers@innovationlabs.com"),
            ("form", "https://startupxyz.com/careers/apply"),
            ("external_site", "https://bigtech.com/jobs/apply"),
            ("direct_url", "https://digitalsolutions.com/careers/apply")
        ]
        
        # Sample requirements and skills
        sample_requirements = [
            ["5+ years of software development experience", "Bachelor's degree in Computer Science", "Experience with modern web technologies"],
            ["3+ years of full-stack development", "Proficiency in JavaScript and Python", "Experience with cloud platforms"],
            ["Strong Python programming skills", "Knowledge of data structures and algorithms", "Experience with databases"],
            ["React.js development experience", "Understanding of modern frontend frameworks", "CSS and HTML expertise"],
            ["DevOps and CI/CD experience", "Knowledge of containerization", "Experience with cloud infrastructure"]
        ]
        
        sample_skills = [
            ["Python", "JavaScript", "React", "Node.js", "PostgreSQL"],
            ["Java", "Spring Boot", "Microservices", "Docker", "AWS"],
            ["Machine Learning", "Python", "TensorFlow", "Data Analysis", "Statistics"],
            ["UI/UX Design", "Figma", "Adobe Creative Suite", "Prototyping", "User Research"],
            ["DevOps", "Kubernetes", "Jenkins", "Terraform", "Monitoring"]
        ]
        
        # Generate mock jobs
        for i in range(15):
            # Select random application method
            app_method, app_url = application_methods[i % len(application_methods)]
            
            # Determine platform based on application method
            if app_method == "email":
                platform = "glassdoor"
            elif app_method == "form":
                platform = "linkedin"
            elif app_method == "external_site":
                platform = "indeed"
            else:
                platform = "mock"
            
            # Create realistic application information
            if app_method == "email":
                apply_url = None
                contact_email = app_url
                contact_phone = "+1 (555) 123-4567"
                external_application = False
            elif app_method == "direct_url":
                apply_url = app_url
                contact_email = f"careers@{sample_companies[i % len(sample_companies)].lower().replace(' ', '').replace('.', '')}.com"
                contact_phone = None
                external_application = True
            else:
                apply_url = app_url
                contact_email = None
                contact_phone = None
                external_application = True
            
            # Generate more realistic description based on keywords
            title = sample_titles[i % len(sample_titles)]
            company = sample_companies[i % len(sample_companies)]
            keywords_mention = ", ".join(request.keywords[:3])  # First 3 keywords
            
            description = (
                f"We are seeking a {title} to join our team at {company}. "
                f"This position requires expertise in {keywords_mention} and related technologies. "
                f"The ideal candidate will have {experience} level experience and be passionate about "
                f"building innovative solutions. This is an excellent opportunity to work on exciting "
                f"projects and grow your career in a dynamic environment."
            )
            
            # Adjust salary based on experience level
            salary_ranges = {
                "entry": "$50,000 - $75,000",
                "junior": "$60,000 - $85,000",
                "mid": "$80,000 - $120,000",
                "senior": "$120,000 - $160,000",
                "lead": "$150,000 - $200,000",
                "executive": "$180,000 - $250,000"
            }
            salary = salary_ranges.get(experience, "$80,000 - $120,000")
            
            # Generate posted dates (vary from recent to a few days ago)
            posted_dates = ["Today", "1 day ago", "2 days ago", "3 days ago", "1 week ago"]
            posted_date = posted_dates[i % len(posted_dates)]
            
            job = Job(
                title=title,
                company=company,
                location=request.location,
                url=f"https://{platform}.com/jobs/{i+1}",
                portal=platform,
                description=description,
                salary=salary,
                posted_date=posted_date,
                experience_level=request.experience_level or "mid",
                requirements=sample_requirements[i % len(sample_requirements)],
                skills=sample_skills[i % len(sample_skills)],
                # Application-related fields
                apply_url=apply_url,
                contact_email=contact_email,
                contact_phone=contact_phone,
                external_application=external_application,
                application_method=app_method,
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
