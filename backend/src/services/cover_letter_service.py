"""Unified cover letter service implementation for the AI Job Application Assistant."""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from ..core.cover_letter_service import CoverLetterService
from ..models.cover_letter import CoverLetter, CoverLetterCreate, CoverLetterUpdate
from ..core.ai_service import AIService
from ..database.repositories.cover_letter_repository import CoverLetterRepository
from loguru import logger


class CoverLetterService(CoverLetterService):
    """Unified cover letter service implementation with AI and template support."""
    
    def __init__(self, ai_service: AIService, repository: Optional[CoverLetterRepository] = None):
        """Initialize the unified cover letter service."""
        self.logger = logger.bind(module="CoverLetterService")
        self.ai_service = ai_service
        self.repository = repository
        # Fallback to in-memory if no repository provided (for backward compatibility)
        if not self.repository:
            self.cover_letters: Dict[str, CoverLetter] = {}  # In-memory storage
    
    async def get_all_cover_letters(self, user_id: Optional[str] = None) -> List[CoverLetter]:
        """Get all cover letters, optionally filtered by user."""
        try:
            if self.repository:
                cover_letters = await self.repository.get_all(user_id=user_id)
            else:
                cover_letters = list(self.cover_letters.values())
                # Sort by creation date, most recent first
                cover_letters.sort(key=lambda c: c.created_at, reverse=True)
            
            self.logger.debug(f"Retrieved {len(cover_letters)} cover letters")
            return cover_letters
            
        except Exception as e:
            self.logger.error(f"Error getting all cover letters: {e}", exc_info=True)
            return []
    
    async def get_cover_letter(self, cover_letter_id: str, user_id: Optional[str] = None) -> Optional[CoverLetter]:
        """Get a specific cover letter by ID, optionally filtered by user."""
        try:
            if self.repository:
                cover_letter = await self.repository.get_by_id(cover_letter_id, user_id=user_id)
            else:
                cover_letter = self.cover_letters.get(cover_letter_id)
            
            if cover_letter:
                self.logger.debug(f"Retrieved cover letter: {cover_letter.job_title} at {cover_letter.company_name}")
            else:
                self.logger.warning(f"Cover letter not found: {cover_letter_id}")
            return cover_letter
            
        except Exception as e:
            self.logger.error(f"Error getting cover letter {cover_letter_id}: {e}", exc_info=True)
            return None
    
    async def create_cover_letter(self, cover_letter_data: CoverLetterCreate, user_id: Optional[str] = None) -> CoverLetter:
        """Create a new cover letter."""
        try:
            cover_letter_id = str(uuid.uuid4())
            
            # Create cover letter object
            cover_letter = CoverLetter(
                id=cover_letter_id,
                job_title=cover_letter_data.job_title,
                company_name=cover_letter_data.company_name,
                content=cover_letter_data.content,
                tone=getattr(cover_letter_data, 'tone', 'professional'),
                word_count=cover_letter_data.word_count or len(cover_letter_data.content.split()),
                file_path=getattr(cover_letter_data, 'file_path', None),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Store cover letter
            if self.repository:
                cover_letter = await self.repository.create(cover_letter, user_id=user_id)
            else:
                self.cover_letters[cover_letter_id] = cover_letter
            
            self.logger.info(f"Cover letter created: {cover_letter.job_title} at {cover_letter.company_name} (ID: {cover_letter.id})")
            return cover_letter
            
        except Exception as e:
            self.logger.error(f"Error creating cover letter: {e}", exc_info=True)
            raise
    
    async def update_cover_letter(self, cover_letter_id: str, updates: CoverLetterUpdate, user_id: Optional[str] = None) -> Optional[CoverLetter]:
        """Update an existing cover letter, optionally filtered by user."""
        try:
            cover_letter = await self.get_cover_letter(cover_letter_id, user_id=user_id)
            if not cover_letter:
                self.logger.warning(f"Cannot update, cover letter not found: {cover_letter_id}")
                return None
            
            # Update allowed fields
            if hasattr(updates, 'job_title') and updates.job_title is not None:
                cover_letter.job_title = updates.job_title
            if hasattr(updates, 'company_name') and updates.company_name is not None:
                cover_letter.company_name = updates.company_name
            if hasattr(updates, 'content') and updates.content is not None:
                cover_letter.content = updates.content
                # Update word count when content changes
                cover_letter.word_count = len(updates.content.split())
            if hasattr(updates, 'tone') and updates.tone is not None:
                cover_letter.tone = updates.tone
            if hasattr(updates, 'word_count') and updates.word_count is not None:
                cover_letter.word_count = updates.word_count
            if hasattr(updates, 'job_description') and updates.job_description is not None:
                cover_letter.job_description = updates.job_description
            if hasattr(updates, 'resume_summary') and updates.resume_summary is not None:
                cover_letter.resume_summary = updates.resume_summary
            
            cover_letter.updated_at = datetime.now(timezone.utc)
            
            # Save to repository if available
            if self.repository:
                update_dict = {}
                if hasattr(updates, 'job_title') and updates.job_title is not None:
                    update_dict['job_title'] = updates.job_title
                if hasattr(updates, 'company_name') and updates.company_name is not None:
                    update_dict['company_name'] = updates.company_name
                if hasattr(updates, 'content') and updates.content is not None:
                    update_dict['content'] = updates.content
                    # Update word count when content changes
                    update_dict['word_count'] = len(updates.content.split())
                if hasattr(updates, 'tone') and updates.tone is not None:
                    update_dict['tone'] = updates.tone
                if updates.word_count is not None:
                    update_dict['word_count'] = updates.word_count
                if update_dict:
                    cover_letter = await self.repository.update(cover_letter_id, update_dict, user_id=user_id)
            
            self.logger.info(f"Cover letter updated: {cover_letter.job_title} at {cover_letter.company_name} (ID: {cover_letter_id})")
            return cover_letter
            
        except Exception as e:
            self.logger.error(f"Error updating cover letter {cover_letter_id}: {e}", exc_info=True)
            return None
    
    async def delete_cover_letter(self, cover_letter_id: str, user_id: Optional[str] = None) -> bool:
        """Delete a cover letter, optionally filtered by user."""
        try:
            cover_letter = await self.get_cover_letter(cover_letter_id, user_id=user_id)
            if not cover_letter:
                self.logger.warning(f"Cannot delete, cover letter not found: {cover_letter_id}")
                return False
            
            # Delete from repository if available
            if self.repository:
                success = await self.repository.delete(cover_letter_id, user_id=user_id)
            else:
                # Remove from memory
                del self.cover_letters[cover_letter_id]
                success = True
            
            self.logger.info(f"Cover letter deleted: {cover_letter.job_title} at {cover_letter.company_name} (ID: {cover_letter_id})")
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting cover letter {cover_letter_id}: {e}", exc_info=True)
            return False

    async def bulk_delete_cover_letters(self, cover_letter_ids: List[str], user_id: Optional[str] = None) -> bool:
        """Delete multiple cover letters."""
        success = True
        try:
            for cl_id in cover_letter_ids:
                result = await self.delete_cover_letter(cl_id, user_id=user_id)
                if not result:
                    success = False
            return success
        except Exception as e:
            self.logger.error(f"Error in bulk cover letter deletion: {e}", exc_info=True)
            return False

    async def generate_cover_letter(
        self, 
        job_title: str, 
        company_name: str, 
        job_description: str, 
        resume_summary: str, 
        tone: str = "professional",
        user_id: Optional[str] = None
    ) -> CoverLetter:
        """Generate a cover letter using AI or templates."""
        try:
            self.logger.info(f"Generating cover letter for {job_title} at {company_name}")
            
            # Try AI generation first
            if await self.ai_service.is_available():
                try:
                    from ..models.cover_letter import CoverLetterRequest
                    
                    # Create AI request
                    ai_request = CoverLetterRequest(
                        job_title=job_title,
                        company_name=company_name,
                        job_description=job_description,
                        resume_summary=resume_summary,
                        tone=tone
                    )
                    
                    # Generate cover letter using AI service
                    generated_cover_letter = await self.ai_service.generate_cover_letter(ai_request)
                    
                    # Create and store the cover letter
                    cover_letter_data = CoverLetterCreate(
                        job_title=job_title,
                        company_name=company_name,
                        content=generated_cover_letter.content,
                        tone=tone,
                        word_count=generated_cover_letter.word_count
                    )
                    
                    cover_letter = await self.create_cover_letter(cover_letter_data, user_id=user_id)
                    
                    self.logger.info(f"AI cover letter generated successfully: {cover_letter.job_title} at {cover_letter.company_name}")
                    return cover_letter
                    
                except Exception as ai_error:
                    self.logger.warning(f"AI generation failed, falling back to template: {ai_error}")
            
            # Fallback to template-based generation
            return await self._generate_template_cover_letter(job_title, company_name, job_description, resume_summary, tone, user_id=user_id)
            
        except Exception as e:
            self.logger.error(f"Error generating cover letter: {e}", exc_info=True)
            raise
    
    async def _generate_template_cover_letter(
        self, 
        job_title: str, 
        company_name: str, 
        job_description: str, 
        resume_summary: str, 
        tone: str = "professional",
        user_id: Optional[str] = None
    ) -> CoverLetter:
        """Generate a template-based cover letter as fallback."""
        try:
            self.logger.info(f"Generating template cover letter for {job_title} at {company_name}")
            
            # Professional template
            if tone.lower() in ['professional', 'formal']:
                content = self._get_professional_template(job_title, company_name, job_description, resume_summary)
            elif tone.lower() in ['casual', 'friendly']:
                content = self._get_casual_template(job_title, company_name, job_description, resume_summary)
            else:
                content = self._get_professional_template(job_title, company_name, job_description, resume_summary)
            
            # Create cover letter
            word_count = len(content.split())
            cover_letter_data = CoverLetterCreate(
                job_title=job_title,
                company_name=company_name,
                content=content,
                tone=tone,
                word_count=word_count
            )
            
            cover_letter = await self.create_cover_letter(cover_letter_data, user_id=user_id)
            
            self.logger.info(f"Template cover letter generated: {cover_letter.job_title} at {cover_letter.company_name}")
            return cover_letter
            
        except Exception as e:
            self.logger.error(f"Error generating template cover letter: {e}", exc_info=True)
            raise
    
    def _get_professional_template(self, job_title: str, company_name: str, job_description: str, resume_summary: str) -> str:
        """Get professional cover letter template."""
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With my background and experience, I am confident that I would be a valuable addition to your team.

{resume_summary}

I am particularly excited about this opportunity at {company_name} because of your company's reputation and the challenging nature of this role. My skills and experience align well with the requirements outlined in your job posting.

I would welcome the opportunity to discuss how my background and enthusiasm can contribute to {company_name}'s continued success. Thank you for your time and consideration.

Sincerely,
[Your Name]"""
    
    def _get_casual_template(self, job_title: str, company_name: str, job_description: str, resume_summary: str) -> str:
        """Get casual cover letter template."""
        return f"""Hello {company_name} Team,

I'm excited to apply for the {job_title} position at {company_name}. I believe my background makes me a great fit for this role.

{resume_summary}

What draws me to {company_name} is your innovative approach and collaborative culture. I'm eager to bring my skills and passion to contribute to your team's success.

I'd love to chat more about how I can help {company_name} achieve its goals. Thanks for considering my application!

Best regards,
[Your Name]"""
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        try:
            cover_letters = await self.get_all_cover_letters()
            ai_available = await self.ai_service.is_available()
            
            return {
                "status": "healthy",
                "available": True,
                "cover_letter_count": len(cover_letters),
                "ai_service_available": ai_available,
                "using_database": self.repository is not None
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "available": False,
                "error": str(e)
            }
