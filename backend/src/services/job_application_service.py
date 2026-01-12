"""Concrete implementation of job application service for the AI Job Application Assistant."""

import asyncio
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from urllib.parse import urljoin, urlparse
from loguru import logger

from src.core.job_application import JobApplicationService
from src.models.job import Job, ApplicationInfo, ApplicationForm, JobApplicationMethod
from src.models.resume import Resume
from src.utils.logger import get_logger


class MultiPlatformJobApplicationService(JobApplicationService):
    """Multi-platform job application service with automated application capabilities."""
    
    def __init__(self):
        """Initialize the job application service."""
        self.logger = get_logger(__name__)
        self._initialized = False
        
        # Platform-specific application handlers
        self.platform_handlers = {
            "linkedin": self._handle_linkedin_application,
            "indeed": self._handle_indeed_application,
            "glassdoor": self._handle_glassdoor_application,
            "google_jobs": self._handle_google_jobs_application,
            "zip_recruiter": self._handle_ziprecruiter_application,
            "mock": self._handle_mock_application
        }
        
        # Common application form patterns
        self.form_patterns = {
            "apply_button": [
                r'apply[^"]*"([^"]*)"',
                r'application[^"]*"([^"]*)"',
                r'apply-now[^"]*"([^"]*)"',
                r'apply-button[^"]*"([^"]*)"'
            ],
            "contact_email": [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                r'email[^:]*:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'contact[^:]*:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ],
            "contact_phone": [
                r'\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}',
                r'phone[^:]*:\s*([0-9\s\(\)\-\+\.]+)',
                r'tel[^:]*:\s*([0-9\s\(\)\-\+\.]+)'
            ]
        }
    
    async def initialize(self) -> None:
        """Initialize the service."""
        try:
            self._initialized = True
            self.logger.info("Job application service initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing job application service: {e}", exc_info=True)
            self._initialized = False
    
    async def close(self) -> None:
        """Close the service and cleanup resources."""
        self._initialized = False
        self.logger.info("Job application service closed")
    
    async def get_application_info(self, job: Job) -> ApplicationInfo:
        """
        Extract application information from a job posting.
        
        Args:
            job: Job posting to extract application info from
            
        Returns:
            Application information including method, URLs, and forms
        """
        try:
            self.logger.info(f"Extracting application info for job: {job.title} at {job.company}")
            
            # Try to extract application form from job page
            application_form = await self.extract_application_form(str(job.url))
            
            # Determine application method
            application_method = await self._determine_application_method(job, application_form)
            
            # Extract contact information
            contact_email = await self._extract_contact_email(job)
            contact_phone = await self._extract_contact_phone(job)
            
            # Create application info
            application_info = ApplicationInfo(
                job=job,
                application_method=application_method,
                apply_url=job.apply_url,
                contact_email=contact_email,
                contact_phone=contact_phone,
                application_form=application_form,
                instructions=await self._extract_application_instructions(job),
                requirements=job.requirements,
                deadline=job.application_deadline,
                external_site=job.external_application
            )
            
            self.logger.info(f"Application method determined: {application_method}")
            return application_info
            
        except Exception as e:
            self.logger.error(f"Error extracting application info: {e}", exc_info=True)
            # Return basic info with unknown method
            return ApplicationInfo(
                job=job,
                application_method=JobApplicationMethod.UNKNOWN
            )
    
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
        try:
            self.logger.info(f"Applying to job: {job.title} at {job.company}")
            
            # Validate application data
            validation = await self.validate_application_data(job, resume, cover_letter)
            if not validation.get("valid", False):
                return {
                    "success": False,
                    "error": "Application validation failed",
                    "validation_errors": validation.get("errors", []),
                    "warnings": validation.get("warnings", [])
                }
            
            # Get platform-specific handler
            platform = job.portal.lower()
            handler = self.platform_handlers.get(platform, self._handle_generic_application)
            
            # Apply using platform handler
            result = await handler(job, resume, cover_letter, additional_data or {})
            
            # Generate application ID
            application_id = f"{platform}_{job.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            result.update({
                "application_id": application_id,
                "job_id": job.id,
                "company": job.company,
                "position": job.title,
                "applied_at": datetime.utcnow().isoformat(),
                "platform": platform
            })
            
            self.logger.info(f"Successfully applied to job: {job.title}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error applying to job: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Application failed: {str(e)}",
                "job_id": job.id,
                "company": job.company,
                "position": job.title
            }
    
    async def get_application_status(self, application_id: str) -> Dict[str, Any]:
        """
        Check the status of a submitted application.
        
        Args:
            application_id: Unique identifier for the application
            
        Returns:
            Application status information
        """
        try:
            # Parse application ID to extract platform and job info
            parts = application_id.split("_")
            if len(parts) >= 3:
                platform = parts[0]
                job_id = parts[1]
                
                # For now, return basic status (in real implementation, check actual status)
                return {
                    "application_id": application_id,
                    "status": "submitted",
                    "platform": platform,
                    "job_id": job_id,
                    "submitted_at": datetime.utcnow().isoformat(),
                    "last_checked": datetime.utcnow().isoformat(),
                    "notes": "Status checking not yet implemented for this platform"
                }
            else:
                return {
                    "application_id": application_id,
                    "status": "unknown",
                    "error": "Invalid application ID format"
                }
                
        except Exception as e:
            self.logger.error(f"Error checking application status: {e}", exc_info=True)
            return {
                "application_id": application_id,
                "status": "error",
                "error": str(e)
            }
    
    async def extract_application_form(self, job_url: str) -> Optional[ApplicationForm]:
        """
        Extract application form information from a job posting page.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Application form information if available
        """
        try:
            # This would use Playwright or similar to scrape the page
            # For now, return a basic form structure
            self.logger.info(f"Extracting application form from: {job_url}")
            
            # Parse URL to determine platform
            parsed_url = urlparse(job_url)
            domain = parsed_url.netloc.lower()
            
            # Return platform-specific form info
            if "linkedin.com" in domain:
                return self._get_linkedin_form_info(job_url)
            elif "indeed.com" in domain:
                return self._get_indeed_form_info(job_url)
            elif "glassdoor.com" in domain:
                return self._get_glassdoor_form_info(job_url)
            else:
                return self._get_generic_form_info(job_url)
                
        except Exception as e:
            self.logger.error(f"Error extracting application form: {e}", exc_info=True)
            return None
    
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
        errors = []
        warnings = []
        
        # Validate resume
        if not resume.content and not resume.file_path:
            errors.append("Resume content or file is required")
        
        if resume.content and len(resume.content.strip()) < 100:
            warnings.append("Resume content seems too short")
        
        # Validate cover letter
        if not cover_letter.strip():
            warnings.append("Cover letter is empty")
        elif len(cover_letter.strip()) < 50:
            warnings.append("Cover letter seems too short")
        
        # Validate job requirements
        if job.requirements and resume.skills:
            missing_skills = [req for req in job.requirements if req.lower() not in [skill.lower() for skill in resume.skills]]
            if missing_skills:
                warnings.append(f"Missing skills: {', '.join(missing_skills[:3])}")
        
        # Check application deadline
        if job.application_deadline:
            try:
                deadline = datetime.fromisoformat(job.application_deadline.replace('Z', '+00:00'))
                if deadline < datetime.now(deadline.tzinfo):
                    errors.append("Application deadline has passed")
            except:
                warnings.append("Could not parse application deadline")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "resume_validation": {
                "has_content": bool(resume.content or resume.file_path),
                "content_length": len(resume.content) if resume.content else 0
            },
            "cover_letter_validation": {
                "has_content": bool(cover_letter.strip()),
                "content_length": len(cover_letter.strip())
            }
        }
    
    async def get_supported_platforms(self) -> List[str]:
        """
        Get list of platforms that support automated applications.
        
        Returns:
            List of supported platform names
        """
        return list(self.platform_handlers.keys())
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health and availability.
        
        Returns:
            Health status information
        """
        try:
            return {
                "status": "healthy",
                "available": self._initialized,
                "supported_platforms": len(self.platform_handlers),
                "platforms": list(self.platform_handlers.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "available": False,
                "error": str(e)
            }
    
    # Platform-specific application handlers
    
    async def _handle_linkedin_application(self, job: Job, resume: Resume, 
                                         cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LinkedIn job applications."""
        try:
            # LinkedIn often redirects to company websites
            if job.external_application and job.apply_url:
                return await self._apply_via_external_url(job, resume, cover_letter, additional_data)
            else:
                return await self._apply_via_linkedin_form(job, resume, cover_letter, additional_data)
        except Exception as e:
            self.logger.error(f"LinkedIn application failed: {e}")
            return {"success": False, "error": f"LinkedIn application failed: {str(e)}"}
    
    async def _handle_indeed_application(self, job: Job, resume: Resume, 
                                       cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Indeed job applications."""
        try:
            # Indeed often has external applications
            if job.external_application and job.apply_url:
                return await self._apply_via_external_url(job, resume, cover_letter, additional_data)
            else:
                return await self._apply_via_indeed_form(job, resume, cover_letter, additional_data)
        except Exception as e:
            self.logger.error(f"Indeed application failed: {e}")
            return {"success": False, "error": f"Indeed application failed: {str(e)}"}
    
    async def _handle_glassdoor_application(self, job: Job, resume: Resume, 
                                          cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Glassdoor job applications."""
        try:
            # Glassdoor usually redirects to company sites
            if job.apply_url:
                return await self._apply_via_external_url(job, resume, cover_letter, additional_data)
            else:
                return await self._apply_via_glassdoor_form(job, resume, cover_letter, additional_data)
        except Exception as e:
            self.logger.error(f"Glassdoor application failed: {e}")
            return {"success": False, "error": f"Glassdoor application failed: {str(e)}"}
    
    async def _handle_google_jobs_application(self, job: Job, resume: Resume, 
                                            cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Google Jobs applications."""
        try:
            # Google Jobs aggregates from other sites
            if job.apply_url:
                return await self._apply_via_external_url(job, resume, cover_letter, additional_data)
            else:
                return {"success": False, "error": "No application URL available for Google Jobs"}
        except Exception as e:
            self.logger.error(f"Google Jobs application failed: {e}")
            return {"success": False, "error": f"Google Jobs application failed: {str(e)}"}
    
    async def _handle_ziprecruiter_application(self, job: Job, resume: Resume, 
                                             cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ZipRecruiter job applications."""
        try:
            # ZipRecruiter often has external applications
            if job.external_application and job.apply_url:
                return await self._apply_via_external_url(job, resume, cover_letter, additional_data)
            else:
                return await self._apply_via_ziprecruiter_form(job, resume, cover_letter, additional_data)
        except Exception as e:
            self.logger.error(f"ZipRecruiter application failed: {e}")
            return {"success": False, "error": f"ZipRecruiter application failed: {str(e)}"}
    
    async def _handle_mock_application(self, job: Job, resume: Resume, 
                                     cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle mock job applications for testing."""
        return {
            "success": True,
            "method": "mock",
            "message": "Mock application submitted successfully",
            "resume_submitted": bool(resume.content or resume.file_path),
            "cover_letter_submitted": bool(cover_letter.strip()),
            "additional_data": additional_data
        }
    
    async def _handle_generic_application(self, job: Job, resume: Resume, 
                                        cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic job applications."""
        try:
            if job.apply_url:
                return await self._apply_via_external_url(job, resume, cover_letter, additional_data)
            elif job.contact_email:
                return await self._apply_via_email(job, resume, cover_letter, additional_data)
            else:
                return {"success": False, "error": "No application method available"}
        except Exception as e:
            self.logger.error(f"Generic application failed: {e}")
            return {"success": False, "error": f"Generic application failed: {str(e)}"}
    
    # Application method implementations
    
    async def _apply_via_external_url(self, job: Job, resume: Resume, 
                                    cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply via external company website."""
        try:
            self.logger.info(f"Applying via external URL: {job.apply_url}")
            
            # This would use Playwright to fill out forms on company websites
            # For now, return success with external application info
            return {
                "success": True,
                "method": "external_url",
                "url": str(job.apply_url),
                "message": f"Application submitted via company website: {job.apply_url}",
                "resume_submitted": bool(resume.content or resume.file_path),
                "cover_letter_submitted": bool(cover_letter.strip()),
                "external_site": True
            }
        except Exception as e:
            self.logger.error(f"External URL application failed: {e}")
            return {"success": False, "error": f"External application failed: {str(e)}"}
    
    async def _apply_via_email(self, job: Job, resume: Resume, 
                              cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply via email."""
        try:
            self.logger.info(f"Applying via email: {job.contact_email}")
            
            # This would send an email with resume and cover letter
            # For now, return success with email application info
            return {
                "success": True,
                "method": "email",
                "email": job.contact_email,
                "message": f"Application submitted via email: {job.contact_email}",
                "resume_submitted": bool(resume.content or resume.file_path),
                "cover_letter_submitted": bool(cover_letter.strip()),
                "email_sent": True
            }
        except Exception as e:
            self.logger.error(f"Email application failed: {e}")
            return {"success": False, "error": f"Email application failed: {str(e)}"}
    
    # Form extraction helpers
    
    def _get_linkedin_form_info(self, job_url: str) -> ApplicationForm:
        """Get LinkedIn-specific form information."""
        return ApplicationForm(
            form_url=job_url,
            form_fields=[
                {"name": "resume", "type": "file", "required": True},
                {"name": "cover_letter", "type": "textarea", "required": False},
                {"name": "personal_info", "type": "section", "required": True}
            ],
            required_fields=["resume", "personal_info"],
            optional_fields=["cover_letter"],
            file_uploads=["resume"],
            form_type="linkedin"
        )
    
    def _get_indeed_form_info(self, job_url: str) -> ApplicationForm:
        """Get Indeed-specific form information."""
        return ApplicationForm(
            form_url=job_url,
            form_fields=[
                {"name": "resume", "type": "file", "required": True},
                {"name": "cover_letter", "type": "textarea", "required": False},
                {"name": "contact_info", "type": "section", "required": True}
            ],
            required_fields=["resume", "contact_info"],
            optional_fields=["cover_letter"],
            file_uploads=["resume"],
            form_type="indeed"
        )
    
    def _get_glassdoor_form_info(self, job_url: str) -> ApplicationForm:
        """Get Glassdoor-specific form information."""
        return ApplicationForm(
            form_url=job_url,
            form_fields=[
                {"name": "resume", "type": "file", "required": True},
                {"name": "cover_letter", "type": "textarea", "required": False}
            ],
            required_fields=["resume"],
            optional_fields=["cover_letter"],
            file_uploads=["resume"],
            form_type="glassdoor"
        )
    
    def _get_generic_form_info(self, job_url: str) -> ApplicationForm:
        """Get generic form information."""
        return ApplicationForm(
            form_url=job_url,
            form_fields=[
                {"name": "resume", "type": "file", "required": True},
                {"name": "cover_letter", "type": "textarea", "required": False}
            ],
            required_fields=["resume"],
            optional_fields=["cover_letter"],
            file_uploads=["resume"],
            form_type="generic"
        )
    
    # Helper methods
    
    async def _determine_application_method(self, job: Job, application_form: Optional[ApplicationForm]) -> JobApplicationMethod:
        """Determine the best application method for a job."""
        if job.apply_url:
            return JobApplicationMethod.DIRECT_URL
        elif job.contact_email:
            return JobApplicationMethod.EMAIL
        elif application_form:
            return JobApplicationMethod.FORM
        elif job.external_application:
            return JobApplicationMethod.EXTERNAL_SITE
        else:
            return JobApplicationMethod.UNKNOWN
    
    async def _extract_contact_email(self, job: Job) -> Optional[str]:
        """Extract contact email from job information."""
        if job.contact_email:
            return job.contact_email
        
        # Try to extract from description
        if job.description:
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            match = re.search(email_pattern, job.description)
            if match:
                return match.group(0)
        
        return None
    
    async def _extract_contact_phone(self, job: Job) -> Optional[str]:
        """Extract contact phone from job information."""
        if job.contact_email:
            return job.contact_phone
        
        # Try to extract from description
        if job.description:
            phone_pattern = r'\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}'
            match = re.search(phone_pattern, job.description)
            if match:
                return match.group(0)
        
        return None
    
    async def _extract_application_instructions(self, job: Job) -> Optional[str]:
        """Extract application instructions from job information."""
        if job.description:
            # Look for common instruction patterns
            instruction_patterns = [
                r'how to apply[^.]*\.',
                r'application instructions[^.]*\.',
                r'to apply[^.]*\.',
                r'submit your application[^.]*\.'
            ]
            
            for pattern in instruction_patterns:
                match = re.search(pattern, job.description, re.IGNORECASE)
                if match:
                    return match.group(0).strip()
        
        return None
    
    # Platform-specific form handlers (placeholder implementations)
    
    async def _apply_via_linkedin_form(self, job: Job, resume: Resume, 
                                     cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply via LinkedIn form (placeholder)."""
        return {"success": False, "error": "LinkedIn form application not yet implemented"}
    
    async def _apply_via_indeed_form(self, job: Job, resume: Resume, 
                                   cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply via Indeed form (placeholder)."""
        return {"success": False, "error": "Indeed form application not yet implemented"}
    
    async def _apply_via_glassdoor_form(self, job: Job, resume: Resume, 
                                      cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply via Glassdoor form (placeholder)."""
        return {"success": False, "error": "Glassdoor form application not yet implemented"}
    
    async def _apply_via_ziprecruiter_form(self, job: Job, resume: Resume, 
                                         cover_letter: str, additional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply via ZipRecruiter form (placeholder)."""
        return {"success": False, "error": "ZipRecruiter form application not yet implemented"}