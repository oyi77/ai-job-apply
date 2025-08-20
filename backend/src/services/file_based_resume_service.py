"""File-based resume service implementation for the AI Job Application Assistant."""

import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import PyPDF2
import docx
import io

from ..core.resume_service import ResumeService
from ..models.resume import Resume
from ..services.local_file_service import LocalFileService
from ..config import config
from ..utils.logger import get_logger
from ..utils.text_processing import extract_skills, clean_text


class FileBasedResumeService(ResumeService):
    """File-based implementation of ResumeService."""
    
    def __init__(self, file_service: Optional[LocalFileService] = None):
        """Initialize the file-based resume service."""
        self.logger = get_logger(__name__)
        self.file_service = file_service or LocalFileService()
        self.resumes: Dict[str, Resume] = {}  # In-memory storage for demo
        self.default_resume_id: Optional[str] = None
    
    async def upload_resume(self, file_path: str, name: str) -> Resume:
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
            max_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
            if file_size and file_size > max_size_bytes:
                raise ValueError(f"File too large. Maximum size: {config.MAX_FILE_SIZE_MB}MB")
            
            # Extract text content
            content = await self.extract_text_from_file(file_path)
            
            # Extract skills from content
            skills = extract_skills(content) if content else []
            
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
                education=self._extract_education(content) if content else None,
                certifications=self._extract_certifications(content) if content else None,
                is_default=len(self.resumes) == 0,  # First resume is default
            )
            
            # Store resume
            self.resumes[resume_id] = resume
            
            # Set as default if it's the first resume
            if resume.is_default:
                self.default_resume_id = resume_id
            
            self.logger.info(f"Resume uploaded successfully: {resume.name} (ID: {resume_id})")
            return resume
            
        except Exception as e:
            self.logger.error(f"Error uploading resume {name}: {e}", exc_info=True)
            raise
    
    async def get_resume(self, resume_id: str) -> Optional[Resume]:
        """Get a resume by ID."""
        try:
            resume = self.resumes.get(resume_id)
            if resume:
                self.logger.debug(f"Retrieved resume: {resume.name} (ID: {resume_id})")
            else:
                self.logger.warning(f"Resume not found: {resume_id}")
            return resume
            
        except Exception as e:
            self.logger.error(f"Error getting resume {resume_id}: {e}", exc_info=True)
            return None
    
    async def get_all_resumes(self) -> List[Resume]:
        """Get all available resumes."""
        try:
            resumes = list(self.resumes.values())
            # Sort by creation date, most recent first
            resumes.sort(key=lambda r: r.created_at, reverse=True)
            
            self.logger.debug(f"Retrieved {len(resumes)} resumes")
            return resumes
            
        except Exception as e:
            self.logger.error(f"Error getting all resumes: {e}", exc_info=True)
            return []
    
    async def get_default_resume(self) -> Optional[Resume]:
        """Get the default resume."""
        try:
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
    
    async def set_default_resume(self, resume_id: str) -> bool:
        """Set a resume as the default."""
        try:
            resume = await self.get_resume(resume_id)
            if not resume:
                self.logger.warning(f"Cannot set default, resume not found: {resume_id}")
                return False
            
            # Unset current default
            if self.default_resume_id:
                current_default = self.resumes.get(self.default_resume_id)
                if current_default:
                    current_default.is_default = False
            
            # Set new default
            resume.is_default = True
            resume.updated_at = datetime.utcnow()
            self.default_resume_id = resume_id
            
            self.logger.info(f"Set default resume: {resume.name} (ID: {resume_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting default resume {resume_id}: {e}", exc_info=True)
            return False
    
    async def delete_resume(self, resume_id: str) -> bool:
        """Delete a resume."""
        try:
            resume = await self.get_resume(resume_id)
            if not resume:
                self.logger.warning(f"Cannot delete, resume not found: {resume_id}")
                return False
            
            # Delete the file
            if await self.file_service.file_exists(resume.file_path):
                await self.file_service.delete_file(resume.file_path)
            
            # Remove from memory
            del self.resumes[resume_id]
            
            # Update default if necessary
            if self.default_resume_id == resume_id:
                self.default_resume_id = None
                # Set another resume as default if available
                remaining_resumes = await self.get_all_resumes()
                if remaining_resumes:
                    await self.set_default_resume(remaining_resumes[0].id)
            
            self.logger.info(f"Resume deleted: {resume.name} (ID: {resume_id})")
            return True
            
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
    
    async def update_resume(self, resume_id: str, updates: dict) -> Optional[Resume]:
        """Update resume information."""
        try:
            resume = await self.get_resume(resume_id)
            if not resume:
                self.logger.warning(f"Cannot update, resume not found: {resume_id}")
                return None
            
            # Update allowed fields
            if 'name' in updates:
                resume.name = updates['name']
            if 'is_default' in updates and updates['is_default']:
                await self.set_default_resume(resume_id)
            
            resume.updated_at = datetime.utcnow()
            
            self.logger.info(f"Resume updated: {resume.name} (ID: {resume_id})")
            return resume
            
        except Exception as e:
            self.logger.error(f"Error updating resume {resume_id}: {e}", exc_info=True)
            return None
    
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
    
    def _extract_education(self, content: str) -> Optional[List[str]]:
        """Extract education information from resume content."""
        try:
            import re
            
            education = []
            content_lower = content.lower()
            
            # Look for degree patterns
            degree_patterns = [
                r'(bachelor[\'s]*\s+(?:of\s+)?(?:science|arts|engineering|computer science))',
                r'(master[\'s]*\s+(?:of\s+)?(?:science|arts|engineering|computer science))',
                r'(phd|ph\.d\.?|doctorate)',
                r'(associate[\'s]*\s+degree)',
                r'(b\.?s\.?|b\.?a\.?|m\.?s\.?|m\.?a\.?|m\.?eng\.?)',
            ]
            
            for pattern in degree_patterns:
                matches = re.findall(pattern, content_lower)
                education.extend(matches)
            
            # Look for university/college names (basic pattern)
            university_patterns = [
                r'university\s+of\s+\w+',
                r'\w+\s+university',
                r'\w+\s+college',
                r'\w+\s+institute\s+of\s+technology',
            ]
            
            for pattern in university_patterns:
                matches = re.findall(pattern, content_lower)
                education.extend(matches)
            
            return list(set(education)) if education else None
            
        except Exception as e:
            self.logger.error(f"Error extracting education: {e}", exc_info=True)
            return None
    
    def _extract_certifications(self, content: str) -> Optional[List[str]]:
        """Extract certifications from resume content."""
        try:
            import re
            
            certifications = []
            content_lower = content.lower()
            
            # Common certification patterns
            cert_patterns = [
                r'aws\s+certified\s+\w+',
                r'microsoft\s+certified\s+\w+',
                r'google\s+certified\s+\w+',
                r'oracle\s+certified\s+\w+',
                r'cisco\s+certified\s+\w+',
                r'pmp\s+certified',
                r'scrum\s+master\s+certified',
                r'certified\s+\w+\s+\w+',
            ]
            
            for pattern in cert_patterns:
                matches = re.findall(pattern, content_lower)
                certifications.extend(matches)
            
            return list(set(certifications)) if certifications else None
            
        except Exception as e:
            self.logger.error(f"Error extracting certifications: {e}", exc_info=True)
            return None
