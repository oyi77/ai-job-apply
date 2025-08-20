"""Resume repository for database operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload

from ..models import DBResume, DBJobApplication
from ...models.resume import Resume
from ...utils.logger import get_logger


class ResumeRepository:
    """Repository for resume database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
        self.logger = get_logger(__name__)
    
    async def create(self, resume: Resume) -> Resume:
        """Create a new resume."""
        try:
            db_resume = DBResume.from_model(resume)
            self.session.add(db_resume)
            await self.session.commit()
            await self.session.refresh(db_resume)
            
            self.logger.info(f"Created resume: {resume.name}")
            return db_resume.to_model()
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating resume: {e}", exc_info=True)
            raise
    
    async def get_by_id(self, resume_id: str) -> Optional[Resume]:
        """Get resume by ID."""
        try:
            stmt = select(DBResume).options(
                selectinload(DBResume.applications)
            ).where(DBResume.id == resume_id)
            
            result = await self.session.execute(stmt)
            db_resume = result.scalar_one_or_none()
            
            if db_resume:
                self.logger.debug(f"Retrieved resume: {db_resume.name}")
                return db_resume.to_model()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting resume {resume_id}: {e}", exc_info=True)
            return None
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Resume]:
        """Get all resumes with optional pagination."""
        try:
            stmt = select(DBResume).options(
                selectinload(DBResume.applications)
            ).order_by(DBResume.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)
            
            result = await self.session.execute(stmt)
            db_resumes = result.scalars().all()
            
            resumes = [resume.to_model() for resume in db_resumes]
            self.logger.debug(f"Retrieved {len(resumes)} resumes")
            
            return resumes
            
        except Exception as e:
            self.logger.error(f"Error getting all resumes: {e}", exc_info=True)
            return []
    
    async def get_by_name(self, name: str) -> Optional[Resume]:
        """Get resume by name."""
        try:
            stmt = select(DBResume).options(
                selectinload(DBResume.applications)
            ).where(DBResume.name == name)
            
            result = await self.session.execute(stmt)
            db_resume = result.scalar_one_or_none()
            
            if db_resume:
                self.logger.debug(f"Retrieved resume by name: {name}")
                return db_resume.to_model()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting resume by name {name}: {e}", exc_info=True)
            return None
    
    async def get_default_resume(self) -> Optional[Resume]:
        """Get the default resume."""
        try:
            stmt = select(DBResume).options(
                selectinload(DBResume.applications)
            ).where(DBResume.is_default == True)
            
            result = await self.session.execute(stmt)
            db_resume = result.scalar_one_or_none()
            
            if db_resume:
                self.logger.debug(f"Retrieved default resume: {db_resume.name}")
                return db_resume.to_model()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting default resume: {e}", exc_info=True)
            return None
    
    async def set_default_resume(self, resume_id: str) -> bool:
        """Set a resume as the default resume."""
        try:
            # First, unset all other default resumes
            await self.session.execute(
                update(DBResume).where(DBResume.is_default == True).values(is_default=False)
            )
            
            # Set the specified resume as default
            result = await self.session.execute(
                update(DBResume).where(DBResume.id == resume_id).values(is_default=True, updated_at=datetime.utcnow())
            )
            
            await self.session.commit()
            
            if result.rowcount > 0:
                self.logger.info(f"Set resume as default: {resume_id}")
                return True
            
            self.logger.warning(f"Resume not found for setting as default: {resume_id}")
            return False
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error setting default resume {resume_id}: {e}", exc_info=True)
            return False
    
    async def update(self, resume_id: str, updates: Dict[str, Any]) -> Optional[Resume]:
        """Update resume."""
        try:
            # Prepare update data
            update_data = {**updates}
            update_data["updated_at"] = datetime.utcnow()
            
            # Handle JSON fields
            if "skills" in update_data and update_data["skills"] is not None:
                import json
                update_data["skills"] = json.dumps(update_data["skills"])
            
            if "education" in update_data and update_data["education"] is not None:
                import json
                update_data["education"] = json.dumps(update_data["education"])
            
            if "certifications" in update_data and update_data["certifications"] is not None:
                import json
                update_data["certifications"] = json.dumps(update_data["certifications"])
            
            # Perform update
            stmt = update(DBResume).where(
                DBResume.id == resume_id
            ).values(**update_data)
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                # Return updated resume
                updated_resume = await self.get_by_id(resume_id)
                self.logger.info(f"Updated resume: {resume_id}")
                return updated_resume
            
            self.logger.warning(f"Resume not found for update: {resume_id}")
            return None
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating resume {resume_id}: {e}", exc_info=True)
            return None
    
    async def delete(self, resume_id: str) -> bool:
        """Delete resume."""
        try:
            stmt = delete(DBResume).where(DBResume.id == resume_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                self.logger.info(f"Deleted resume: {resume_id}")
                return True
            
            self.logger.warning(f"Resume not found for deletion: {resume_id}")
            return False
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error deleting resume {resume_id}: {e}", exc_info=True)
            return False
    
    async def search(self, query: str, limit: Optional[int] = None) -> List[Resume]:
        """Search resumes by name, content, or skills."""
        try:
            search_term = f"%{query.lower()}%"
            
            stmt = select(DBResume).options(
                selectinload(DBResume.applications)
            ).where(
                or_(
                    func.lower(DBResume.name).like(search_term),
                    func.lower(DBResume.content).like(search_term),
                    func.lower(DBResume.skills).like(search_term)
                )
            ).order_by(DBResume.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            db_resumes = result.scalars().all()
            
            resumes = [resume.to_model() for resume in db_resumes]
            self.logger.debug(f"Found {len(resumes)} resumes matching '{query}'")
            
            return resumes
            
        except Exception as e:
            self.logger.error(f"Error searching resumes with query '{query}': {e}", exc_info=True)
            return []
    
    async def get_by_file_type(self, file_type: str, limit: Optional[int] = None) -> List[Resume]:
        """Get resumes by file type."""
        try:
            stmt = select(DBResume).options(
                selectinload(DBResume.applications)
            ).where(
                func.lower(DBResume.file_type) == file_type.lower()
            ).order_by(DBResume.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            db_resumes = result.scalars().all()
            
            resumes = [resume.to_model() for resume in db_resumes]
            self.logger.debug(f"Retrieved {len(resumes)} resumes with file type {file_type}")
            
            return resumes
            
        except Exception as e:
            self.logger.error(f"Error getting resumes by file type {file_type}: {e}", exc_info=True)
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get resume statistics."""
        try:
            # Get total count
            total_stmt = select(func.count(DBResume.id))
            total_result = await self.session.execute(total_stmt)
            total_resumes = total_result.scalar()
            
            # Get file type breakdown
            file_type_stmt = select(
                DBResume.file_type,
                func.count(DBResume.id)
            ).group_by(DBResume.file_type)
            
            file_type_result = await self.session.execute(file_type_stmt)
            file_type_breakdown = dict(file_type_result.all())
            
            # Get default resume count
            default_stmt = select(func.count(DBResume.id)).where(DBResume.is_default == True)
            default_result = await self.session.execute(default_stmt)
            default_count = default_result.scalar()
            
            # Get recent activity (last 30 days)
            from datetime import timedelta
            recent_cutoff = datetime.utcnow() - timedelta(days=30)
            recent_stmt = select(func.count(DBResume.id)).where(
                DBResume.created_at >= recent_cutoff
            )
            recent_result = await self.session.execute(recent_stmt)
            recent_resumes = recent_result.scalar()
            
            # Get resumes with skills
            skills_stmt = select(func.count(DBResume.id)).where(
                DBResume.skills.is_not(None)
            )
            skills_result = await self.session.execute(skills_stmt)
            resumes_with_skills = skills_result.scalar()
            
            stats = {
                "total_resumes": total_resumes,
                "file_type_breakdown": file_type_breakdown,
                "default_resumes": default_count,
                "recent_activity": f"{recent_resumes} resumes in the last 30 days",
                "resumes_with_skills": resumes_with_skills,
                "skill_coverage": (resumes_with_skills / total_resumes * 100) if total_resumes > 0 else 0,
            }
            
            self.logger.debug("Generated resume statistics from database")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting resume stats: {e}", exc_info=True)
            return {
                "total_resumes": 0,
                "file_type_breakdown": {},
                "recent_activity": "0 resumes in the last 30 days",
                "error": str(e)
            }
    
    async def get_resumes_with_experience(self, min_years: int, max_years: Optional[int] = None) -> List[Resume]:
        """Get resumes by experience level."""
        try:
            conditions = [DBResume.experience_years >= min_years]
            
            if max_years is not None:
                conditions.append(DBResume.experience_years <= max_years)
            
            stmt = select(DBResume).options(
                selectinload(DBResume.applications)
            ).where(and_(*conditions)).order_by(DBResume.experience_years.desc())
            
            result = await self.session.execute(stmt)
            db_resumes = result.scalars().all()
            
            resumes = [resume.to_model() for resume in db_resumes]
            self.logger.debug(f"Retrieved {len(resumes)} resumes with {min_years}+ years experience")
            
            return resumes
            
        except Exception as e:
            self.logger.error(f"Error getting resumes by experience: {e}", exc_info=True)
            return []
