"""Unified resume service implementation for the AI Job Application Assistant."""

import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import PyPDF2
import docx
import io
import json

from src.core.cache import cache_region
from src.core.resume_service import ResumeService
from src.models.resume import Resume
from src.services.local_file_service import LocalFileService
from src.database.repositories.resume_repository import ResumeRepository
from src.config import config
from loguru import logger
from src.utils.text_processing import extract_skills, clean_text


class ResumeService(ResumeService):
    """Unified implementation of ResumeService with file and database support."""
    
    def __init__(self, file_service: LocalFileService, repository: Optional[ResumeRepository] = None):
        """Initialize the unified resume service."""
        self.logger = logger.bind(module="ResumeService")
        self.file_service = file_service
        self.repository = repository
        # Fallback to in-memory if no repository provided (for backward compatibility)
        if not self.repository:
            self.resumes: Dict[str, Resume] = {}  # In-memory cache
            self.default_resume_id: Optional[str] = None
            self._initialize_sample_data()
    
    def _initialize_sample_data(self) -> None:
        """Initialize with sample data for demonstration."""
        sample_resume = Resume(
            id=str(uuid.uuid4()),
            name="Sample Resume",
            file_path="./resumes/sample_resume.pdf",
            file_type="pdf",
            content="Experienced software developer with expertise in Python, JavaScript, and cloud technologies.",
            skills=["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"],
            experience_years=5,
            education=["Bachelor of Science in Computer Science"],
            certifications=["AWS Certified Developer", "Scrum Master Certified"],
            is_default=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.resumes[sample_resume.id] = sample_resume
        self.default_resume_id = sample_resume.id
        self.logger.info("Initialized with sample resume data")
    
    async def upload_resume(self, file_path: str, name: str, user_id: Optional[str] = None) -> Resume:
        """Upload and process a new resume."""
        try:
            self.logger.info(f"Uploading resume: {name}")
            
            # Validate file exists
            if not await self.file_service.file_exists(file_path):
                raise FileNotFoundError(f"Resume file not found: {file_path}")
            
            # Get file info
            file_info = await self.file_service.get_file_info(file_path)
            if not file_info:
                raise ValueError(f"Could not get file info for: {file_path}")
            
            # Validate file type
            allowed_types = [".pdf", ".docx", ".txt"]
            if not await self.file_service.is_valid_file_type(file_path, allowed_types):
                raise ValueError(f"Unsupported file type. Allowed types: {allowed_types}")
            
            # Validate file size
            file_size = await self.file_service.get_file_size(file_path)
            max_size_bytes = getattr(config, 'max_file_size', 10 * 1024 * 1024)  # Default 10MB
            if file_size and file_size > max_size_bytes:
                max_size_mb = max_size_bytes // (1024 * 1024)
                raise ValueError(f"File too large. Maximum size: {max_size_mb}MB")
            
            # Extract text content
            content = await self.extract_text_from_file(file_path)
            
            # Extract skills from content
            skills = extract_skills(content) if content else []
            
            # Enhanced extraction using AI if available (for better accuracy)
            education = None
            certifications = None
            if content:
                # Try AI extraction first (if AI service is available)
                try:
                    from src.services.service_registry import service_registry
                    ai_service = await service_registry.get_ai_service()
                    if await ai_service.is_available():
                        # Use AI to extract education and certifications more accurately
                        education_prompt = f"Extract all education information (degrees, universities, graduation dates) from this resume. Return only a JSON array of education entries:\n\n{content[:2000]}"
                        cert_prompt = f"Extract all certifications and professional credentials from this resume. Return only a JSON array of certification names:\n\n{content[:2000]}"
                        
                        # Try to get education via AI (non-blocking - fallback to regex if fails)
                        try:
                            from src.core.ai_provider import AIResponse
                            # This is a simplified approach - in production, you'd want a dedicated extraction method
                            education = self._extract_education(content)  # Fallback to regex for now
                            certifications = self._extract_certifications(content)  # Fallback to regex for now
                        except:
                            education = self._extract_education(content)
                            certifications = self._extract_certifications(content)
                    else:
                        education = self._extract_education(content)
                        certifications = self._extract_certifications(content)
                except Exception as e:
                    self.logger.warning(f"AI extraction not available, using regex: {e}")
                    education = self._extract_education(content)
                    certifications = self._extract_certifications(content)
            
            # Check if this is the first resume (for default setting)
            is_first_resume = False
            if self.repository:
                all_resumes = await self.repository.get_all()
                is_first_resume = len(all_resumes) == 0
            else:
                is_first_resume = len(self.resumes) == 0
            
            # Create resume object
            resume_id = str(uuid.uuid4())
            resume = Resume(
                id=resume_id,
                name=name,
                file_path=file_path,
                file_type=file_info["extension"].lstrip('.'),
                content=content,
                skills=skills,
                experience_years=self._estimate_experience_years(content) if content else None,
                education=education or [],
                certifications=certifications or [],
                is_default=is_first_resume,  # First resume is default
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Store resume
            if self.repository:
                resume = await self.repository.create(resume, user_id=user_id)
            else:
                self.resumes[resume_id] = resume
                # Set as default if it's the first resume
                if resume.is_default:
                    self.default_resume_id = resume_id
            
            # Invalidate cache
            if user_id:
                cache_region.delete(f"user_resumes:{user_id}")
            
            self.logger.info(f"Resume uploaded successfully: {resume.name} (ID: {resume.id})")
            return resume
            
        except Exception as e:
            self.logger.error(f"Error uploading resume {name}: {e}", exc_info=True)
            raise
    
    async def get_resume(self, resume_id: str, user_id: Optional[str] = None) -> Optional[Resume]:
        """Get a resume by ID, optionally filtered by user."""
        try:
            # Try to get from cache first
            cache_key = f"resume:{resume_id}"
            cached_resume = cache_region.get(cache_key)
            if cached_resume is not list: # dogpile returns NO_VALUE (which is not list) on miss? No, it returns NO_VALUE object.
                 # Actually, let's use the standard check.
                 pass

            if cached_resume and not isinstance(cached_resume, type(cache_region.dogpile_registry.get("NO_VALUE"))):
                 self.logger.debug(f"Cache hit for resume: {resume_id}")
                 # Ensure it matches user_id if provided
                 if user_id and cached_resume.user_id != user_id:
                     self.logger.warning(f"Cached resume {resume_id} does not match user {user_id}")
                 else:
                     return cached_resume

            if self.repository:
                resume = await self.repository.get_by_id(resume_id, user_id=user_id)
            else:
                resume = self.resumes.get(resume_id)
            
            if resume:
                self.logger.debug(f"Retrieved resume: {resume.name} (ID: {resume_id})")
                # Cache the result
                cache_region.set(cache_key, resume)
            else:
                self.logger.warning(f"Resume not found: {resume_id}")
            return resume
            
        except Exception as e:
            self.logger.error(f"Error getting resume {resume_id}: {e}", exc_info=True)
            return None
    
    async def get_all_resumes(self, user_id: Optional[str] = None) -> List[Resume]:
        """Get all available resumes, optionally filtered by user."""
        try:
            if user_id:
                cache_key = f"user_resumes:{user_id}"
                cached_resumes = cache_region.get(cache_key)
                if cached_resumes and not isinstance(cached_resumes, type(cache_region.dogpile_registry.get("NO_VALUE"))):
                    self.logger.debug(f"Cache hit for user_resumes:{user_id}")
                    return cached_resumes

            if self.repository:
                resumes = await self.repository.get_all(user_id=user_id)
            else:
                resumes = list(self.resumes.values())
                # Sort by creation date, most recent first
                resumes.sort(key=lambda r: r.created_at, reverse=True)
            
            self.logger.debug(f"Retrieved {len(resumes)} resumes")
            
            # Cache the result if user_id is provided
            if user_id:
                cache_region.set(f"user_resumes:{user_id}", resumes)
                
            return resumes
            
        except Exception as e:
            self.logger.error(f"Error getting all resumes: {e}", exc_info=True)
            return []
    
    async def get_default_resume(self, user_id: Optional[str] = None) -> Optional[Resume]:
        """Get the default resume, optionally filtered by user."""
        try:
            if self.repository:
                return await self.repository.get_default_resume(user_id=user_id)
            
            # Fallback to in-memory
            if self.default_resume_id:
                return await self.get_resume(self.default_resume_id)
            
            # If no default set, return the first resume
            resumes = await self.get_all_resumes()
            if resumes:
                return resumes[0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting default resume: {e}", exc_info=True)
            return None
    
    async def set_default_resume(self, resume_id: str, user_id: Optional[str] = None) -> bool:
        """Set a resume as the default."""
        try:
            resume = await self.get_resume(resume_id, user_id=user_id)
            if not resume:
                self.logger.warning(f"Cannot set default, resume not found: {resume_id}")
                return False
            
            if self.repository:
                return await self.repository.set_default_resume(resume_id, user_id=user_id)
            
            # Fallback to in-memory
            # Unset current default
            if self.default_resume_id:
                current_default = self.resumes.get(self.default_resume_id)
                if current_default:
                    current_default.is_default = False
            
            # Set new default
            resume.is_default = True
            resume.updated_at = datetime.now(timezone.utc)
            self.default_resume_id = resume_id
            
            self.logger.info(f"Set default resume: {resume.name} (ID: {resume_id})")
            
            # Invalidate cache
            if user_id:
                # We need to invalidate the list because 'is_default' field changed for multiple resumes
                cache_region.delete(f"user_resumes:{user_id}")
                # And the specific resume
                cache_region.delete(f"resume:{resume_id}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting default resume {resume_id}: {e}", exc_info=True)
            return False
    
    async def delete_resume(self, resume_id: str, user_id: Optional[str] = None) -> bool:
        """Delete a resume."""
        try:
            resume = await self.get_resume(resume_id, user_id=user_id)
            if not resume:
                self.logger.warning(f"Cannot delete, resume not found: {resume_id}")
                return False
            
            # Delete the file
            if await self.file_service.file_exists(resume.file_path):
                await self.file_service.delete_file(resume.file_path)
            
            # Delete from repository if available
            if self.repository:
                success = await self.repository.delete(resume_id, user_id=user_id)
            else:
                # Remove from memory
                del self.resumes[resume_id]
                
                # Update default if necessary
                if self.default_resume_id == resume_id:
                    self.default_resume_id = None
                    # Set another resume as default if available
                    remaining_resumes = await self.get_all_resumes()
                    if remaining_resumes:
                        await self.set_default_resume(remaining_resumes[0].id)
                success = True
            
            self.logger.info(f"Resume deleted: {resume.name} (ID: {resume_id})")
            
            # Invalidate cache
            if user_id:
                cache_region.delete(f"user_resumes:{user_id}")
            cache_region.delete(f"resume:{resume_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting resume {resume_id}: {e}", exc_info=True)
            return False
    
    async def extract_text(self, resume: Resume) -> str:
        """Extract text content from resume file."""
        try:
            if resume.content:
                return resume.content
            
            return await self.extract_text_from_file(resume.file_path)
            
        except Exception as e:
            self.logger.error(f"Error extracting text from resume {resume.id}: {e}", exc_info=True)
            return ""
    
    async def extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from various file formats."""
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                return await self._extract_text_from_pdf(file_path)
            elif file_extension == '.docx':
                return await self._extract_text_from_docx(file_path)
            elif file_extension == '.txt':
                return await self._extract_text_from_txt(file_path)
            else:
                self.logger.warning(f"Unsupported file type for text extraction: {file_extension}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error extracting text from file {file_path}: {e}", exc_info=True)
            return ""
    
    async def update_resume(self, resume_id: str, updates: dict, user_id: Optional[str] = None) -> Optional[Resume]:
        """Update resume information."""
        try:
            resume = await self.get_resume(resume_id, user_id=user_id)
            if not resume:
                self.logger.warning(f"Cannot update, resume not found: {resume_id}")
                return None
            
            # Update allowed fields
            if 'name' in updates:
                resume.name = updates['name']
            if 'is_default' in updates and updates['is_default']:
                await self.set_default_resume(resume_id)
            
            resume.updated_at = datetime.now(timezone.utc)
            
            # Save to repository if available
            if self.repository:
                update_dict = {}
                if 'name' in updates:
                    update_dict['name'] = updates['name']
                if update_dict:
                    resume = await self.repository.update(resume_id, update_dict, user_id=user_id)
            
            self.logger.info(f"Resume updated: {resume.name} (ID: {resume_id})")
            
            # Invalidate cache
            if user_id:
                cache_region.delete(f"user_resumes:{user_id}")
            cache_region.delete(f"resume:{resume_id}")
            
            return resume
            
        except Exception as e:
            self.logger.error(f"Error updating resume {resume_id}: {e}", exc_info=True)
            return None

    async def bulk_delete_resumes(self, resume_ids: List[str], user_id: Optional[str] = None) -> bool:
        """Delete multiple resumes."""
        success = True
        try:
            for resume_id in resume_ids:
                result = await self.delete_resume(resume_id, user_id=user_id)
                if not result:
                    success = False
            return success
        except Exception as e:
            self.logger.error(f"Error in bulk resume deletion: {e}", exc_info=True)
            return False

    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            content = await self.file_service.read_file(file_path)
            if not content:
                return ""
            
            text = ""
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return clean_text(text)
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF {file_path}: {e}", exc_info=True)
            return ""
    
    async def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            content = await self.file_service.read_file(file_path)
            if not content:
                return ""
            
            doc = docx.Document(io.BytesIO(content))
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return clean_text(text)
            
        except Exception as e:
            self.logger.error(f"Error extracting text from DOCX {file_path}: {e}", exc_info=True)
            return ""
    
    async def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            content = await self.file_service.read_file(file_path)
            if not content:
                return ""
            
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    text = content.decode(encoding)
                    return clean_text(text)
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, use error handling
            text = content.decode('utf-8', errors='replace')
            return clean_text(text)
            
        except Exception as e:
            self.logger.error(f"Error extracting text from TXT {file_path}: {e}", exc_info=True)
            return ""
    
    def _estimate_experience_years(self, content: str) -> Optional[int]:
        """Estimate years of experience from resume content."""
        try:
            import re
            
            # Look for patterns like "X years", "X+ years", etc.
            patterns = [
                r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
                r'(\d+)\+?\s*yrs?\s*(?:of\s*)?(?:experience|exp)',
                r'experience.*?(\d+)\+?\s*years?',
                r'(\d+)\+?\s*years?\s*in\s*(?:software|development|programming)',
            ]
            
            years = []
            content_lower = content.lower()
            
            for pattern in patterns:
                matches = re.findall(pattern, content_lower)
                for match in matches:
                    try:
                        years.append(int(match))
                    except ValueError:
                        continue
            
            if years:
                # Return the maximum years found
                return max(years)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error estimating experience years: {e}", exc_info=True)
            return None
    
    def _extract_education(self, content: str) -> List[str]:
        """Extract education information from resume content."""
        try:
            import re
            
            education = []
            if not content:
                return []
            
            content_lower = content.lower()
            
            # Look for degree patterns (case-insensitive, more flexible)
            degree_patterns = [
                r'(bachelor[\'s]*\s+(?:of\s+)?(?:science|arts|engineering|computer\s+science|business|technology))',
                r'(master[\'s]*\s+(?:of\s+)?(?:science|arts|engineering|computer\s+science|business|technology|mba))',
                r'(phd|ph\.d\.?|doctorate)',
                r'(associate[\'s]*\s+degree)',
                r'(b\.?s\.?|b\.?a\.?|m\.?s\.?|m\.?a\.?|m\.?eng\.?|m\.?b\.?a\.?)',
            ]
            
            for pattern in degree_patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                education.extend([m.title() if isinstance(m, str) else m for m in matches])
            
            # Look for university/college names (more flexible patterns)
            university_patterns = [
                r'(university\s+of\s+[a-z\s]+)',
                r'([a-z\s]+university)',
                r'([a-z\s]+college)',
                r'([a-z\s]+institute\s+of\s+technology)',
                r'([a-z\s]+tech)',
            ]
            
            for pattern in university_patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                # Filter out common false positives
                filtered = [m.title().strip() for m in matches if len(m.strip()) > 5 and 'university' in m.lower() or 'college' in m.lower()]
                education.extend(filtered)
            
            # Remove duplicates and return
            unique_education = list(set(education))
            return unique_education if unique_education else []
            
        except Exception as e:
            self.logger.error(f"Error extracting education: {e}", exc_info=True)
            return []
    
    def _extract_certifications(self, content: str) -> List[str]:
        """Extract certifications from resume content."""
        try:
            import re
            
            certifications = []
            if not content:
                return []
            
            content_lower = content.lower()
            
            # Common certification patterns (more comprehensive)
            cert_patterns = [
                r'(aws\s+certified\s+[a-z\s]+)',
                r'(microsoft\s+certified\s+[a-z\s]+)',
                r'(google\s+certified\s+[a-z\s]+)',
                r'(oracle\s+certified\s+[a-z\s]+)',
                r'(cisco\s+certified\s+[a-z\s]+)',
                r'(pmp\s+certified|project\s+management\s+professional)',
                r'(scrum\s+master\s+certified|certified\s+scrum\s+master)',
                r'(certified\s+[a-z\s]+professional)',
                r'(certified\s+[a-z\s]+specialist)',
                r'(certified\s+[a-z\s]+engineer)',
                r'(certified\s+[a-z\s]+developer)',
                r'(certified\s+[a-z\s]+analyst)',
            ]
            
            for pattern in cert_patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                certifications.extend([m.title().strip() if isinstance(m, str) else m for m in matches])
            
            # Also look for common abbreviations
            abbrev_certs = [
                r'\b(pmp)\b',
                r'\b(csm)\b',
                r'\b(cspo)\b',
                r'\b(itil)\b',
                r'\b(ccna|ccnp|ccie)\b',
            ]
            
            for pattern in abbrev_certs:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                certifications.extend([m.upper() for m in matches])
            
            # Remove duplicates and return
            unique_certs = list(set(certifications))
            return unique_certs if unique_certs else []
            
        except Exception as e:
            self.logger.error(f"Error extracting certifications: {e}", exc_info=True)
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        try:
            resumes = await self.get_all_resumes()
            default_resume = await self.get_default_resume()
            return {
                "status": "healthy",
                "available": True,
                "resume_count": len(resumes),
                "default_resume": default_resume is not None,
                "using_database": self.repository is not None
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "available": False,
                "error": str(e)
            }
