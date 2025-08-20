"""Cover letter repository for database operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload

from ..models import DBCoverLetter, DBJobApplication
from ...models.cover_letter import CoverLetter
from ...utils.logger import get_logger


class CoverLetterRepository:
    """Repository for cover letter database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
        self.logger = get_logger(__name__)
    
    async def create(self, cover_letter: CoverLetter) -> CoverLetter:
        """Create a new cover letter."""
        try:
            db_cover_letter = DBCoverLetter.from_model(cover_letter)
            self.session.add(db_cover_letter)
            await self.session.commit()
            await self.session.refresh(db_cover_letter)
            
            self.logger.info(f"Created cover letter for {cover_letter.job_title} at {cover_letter.company_name}")
            return db_cover_letter.to_model()
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating cover letter: {e}", exc_info=True)
            raise
    
    async def get_by_id(self, cover_letter_id: str) -> Optional[CoverLetter]:
        """Get cover letter by ID."""
        try:
            stmt = select(DBCoverLetter).options(
                selectinload(DBCoverLetter.applications)
            ).where(DBCoverLetter.id == cover_letter_id)
            
            result = await self.session.execute(stmt)
            db_cover_letter = result.scalar_one_or_none()
            
            if db_cover_letter:
                self.logger.debug(f"Retrieved cover letter: {db_cover_letter.job_title}")
                return db_cover_letter.to_model()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting cover letter {cover_letter_id}: {e}", exc_info=True)
            return None
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[CoverLetter]:
        """Get all cover letters with optional pagination."""
        try:
            stmt = select(DBCoverLetter).options(
                selectinload(DBCoverLetter.applications)
            ).order_by(DBCoverLetter.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)
            
            result = await self.session.execute(stmt)
            db_cover_letters = result.scalars().all()
            
            cover_letters = [cl.to_model() for cl in db_cover_letters]
            self.logger.debug(f"Retrieved {len(cover_letters)} cover letters")
            
            return cover_letters
            
        except Exception as e:
            self.logger.error(f"Error getting all cover letters: {e}", exc_info=True)
            return []
    
    async def get_by_company(self, company_name: str) -> List[CoverLetter]:
        """Get cover letters by company name."""
        try:
            stmt = select(DBCoverLetter).options(
                selectinload(DBCoverLetter.applications)
            ).where(
                func.lower(DBCoverLetter.company_name) == company_name.lower()
            ).order_by(DBCoverLetter.created_at.desc())
            
            result = await self.session.execute(stmt)
            db_cover_letters = result.scalars().all()
            
            cover_letters = [cl.to_model() for cl in db_cover_letters]
            self.logger.debug(f"Retrieved {len(cover_letters)} cover letters for {company_name}")
            
            return cover_letters
            
        except Exception as e:
            self.logger.error(f"Error getting cover letters for company {company_name}: {e}", exc_info=True)
            return []
    
    async def get_by_job_title(self, job_title: str) -> List[CoverLetter]:
        """Get cover letters by job title."""
        try:
            stmt = select(DBCoverLetter).options(
                selectinload(DBCoverLetter.applications)
            ).where(
                func.lower(DBCoverLetter.job_title) == job_title.lower()
            ).order_by(DBCoverLetter.created_at.desc())
            
            result = await self.session.execute(stmt)
            db_cover_letters = result.scalars().all()
            
            cover_letters = [cl.to_model() for cl in db_cover_letters]
            self.logger.debug(f"Retrieved {len(cover_letters)} cover letters for {job_title}")
            
            return cover_letters
            
        except Exception as e:
            self.logger.error(f"Error getting cover letters for job title {job_title}: {e}", exc_info=True)
            return []
    
    async def get_by_tone(self, tone: str, limit: Optional[int] = None) -> List[CoverLetter]:
        """Get cover letters by tone."""
        try:
            stmt = select(DBCoverLetter).options(
                selectinload(DBCoverLetter.applications)
            ).where(
                func.lower(DBCoverLetter.tone) == tone.lower()
            ).order_by(DBCoverLetter.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            db_cover_letters = result.scalars().all()
            
            cover_letters = [cl.to_model() for cl in db_cover_letters]
            self.logger.debug(f"Retrieved {len(cover_letters)} cover letters with tone {tone}")
            
            return cover_letters
            
        except Exception as e:
            self.logger.error(f"Error getting cover letters by tone {tone}: {e}", exc_info=True)
            return []
    
    async def update(self, cover_letter_id: str, updates: Dict[str, Any]) -> Optional[CoverLetter]:
        """Update cover letter."""
        try:
            # Prepare update data
            update_data = {**updates}
            update_data["updated_at"] = datetime.utcnow()
            
            # Perform update
            stmt = update(DBCoverLetter).where(
                DBCoverLetter.id == cover_letter_id
            ).values(**update_data)
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                # Return updated cover letter
                updated_cover_letter = await self.get_by_id(cover_letter_id)
                self.logger.info(f"Updated cover letter: {cover_letter_id}")
                return updated_cover_letter
            
            self.logger.warning(f"Cover letter not found for update: {cover_letter_id}")
            return None
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating cover letter {cover_letter_id}: {e}", exc_info=True)
            return None
    
    async def delete(self, cover_letter_id: str) -> bool:
        """Delete cover letter."""
        try:
            stmt = delete(DBCoverLetter).where(DBCoverLetter.id == cover_letter_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                self.logger.info(f"Deleted cover letter: {cover_letter_id}")
                return True
            
            self.logger.warning(f"Cover letter not found for deletion: {cover_letter_id}")
            return False
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error deleting cover letter {cover_letter_id}: {e}", exc_info=True)
            return False
    
    async def search(self, query: str, limit: Optional[int] = None) -> List[CoverLetter]:
        """Search cover letters by job title, company, or content."""
        try:
            search_term = f"%{query.lower()}%"
            
            stmt = select(DBCoverLetter).options(
                selectinload(DBCoverLetter.applications)
            ).where(
                or_(
                    func.lower(DBCoverLetter.job_title).like(search_term),
                    func.lower(DBCoverLetter.company_name).like(search_term),
                    func.lower(DBCoverLetter.content).like(search_term)
                )
            ).order_by(DBCoverLetter.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            db_cover_letters = result.scalars().all()
            
            cover_letters = [cl.to_model() for cl in db_cover_letters]
            self.logger.debug(f"Found {len(cover_letters)} cover letters matching '{query}'")
            
            return cover_letters
            
        except Exception as e:
            self.logger.error(f"Error searching cover letters with query '{query}': {e}", exc_info=True)
            return []
    
    async def get_by_word_count_range(self, min_words: int, max_words: Optional[int] = None) -> List[CoverLetter]:
        """Get cover letters by word count range."""
        try:
            conditions = [DBCoverLetter.word_count >= min_words]
            
            if max_words is not None:
                conditions.append(DBCoverLetter.word_count <= max_words)
            
            stmt = select(DBCoverLetter).options(
                selectinload(DBCoverLetter.applications)
            ).where(and_(*conditions)).order_by(DBCoverLetter.word_count.desc())
            
            result = await self.session.execute(stmt)
            db_cover_letters = result.scalars().all()
            
            cover_letters = [cl.to_model() for cl in db_cover_letters]
            self.logger.debug(f"Retrieved {len(cover_letters)} cover letters with {min_words}+ words")
            
            return cover_letters
            
        except Exception as e:
            self.logger.error(f"Error getting cover letters by word count: {e}", exc_info=True)
            return []
    
    async def get_recent(self, days: int = 30, limit: Optional[int] = None) -> List[CoverLetter]:
        """Get recent cover letters."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stmt = select(DBCoverLetter).options(
                selectinload(DBCoverLetter.applications)
            ).where(
                DBCoverLetter.created_at >= cutoff_date
            ).order_by(DBCoverLetter.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            db_cover_letters = result.scalars().all()
            
            cover_letters = [cl.to_model() for cl in db_cover_letters]
            self.logger.debug(f"Retrieved {len(cover_letters)} cover letters from last {days} days")
            
            return cover_letters
            
        except Exception as e:
            self.logger.error(f"Error getting recent cover letters: {e}", exc_info=True)
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get cover letter statistics."""
        try:
            # Get total count
            total_stmt = select(func.count(DBCoverLetter.id))
            total_result = await self.session.execute(total_stmt)
            total_cover_letters = total_result.scalar()
            
            # Get tone breakdown
            tone_stmt = select(
                DBCoverLetter.tone,
                func.count(DBCoverLetter.id)
            ).group_by(DBCoverLetter.tone)
            
            tone_result = await self.session.execute(tone_stmt)
            tone_breakdown = dict(tone_result.all())
            
            # Get average word count
            avg_words_stmt = select(func.avg(DBCoverLetter.word_count))
            avg_words_result = await self.session.execute(avg_words_stmt)
            avg_word_count = avg_words_result.scalar() or 0
            
            # Get word count range
            word_count_range_stmt = select(
                func.min(DBCoverLetter.word_count),
                func.max(DBCoverLetter.word_count)
            )
            word_count_result = await self.session.execute(word_count_range_stmt)
            min_words, max_words = word_count_result.first() or (0, 0)
            
            # Get recent activity (last 30 days)
            recent_cutoff = datetime.utcnow() - timedelta(days=30)
            recent_stmt = select(func.count(DBCoverLetter.id)).where(
                DBCoverLetter.created_at >= recent_cutoff
            )
            recent_result = await self.session.execute(recent_stmt)
            recent_cover_letters = recent_result.scalar()
            
            # Get top companies
            companies_stmt = select(
                DBCoverLetter.company_name,
                func.count(DBCoverLetter.id)
            ).group_by(DBCoverLetter.company_name).order_by(func.count(DBCoverLetter.id).desc()).limit(5)
            
            companies_result = await self.session.execute(companies_stmt)
            top_companies = dict(companies_result.all())
            
            stats = {
                "total_cover_letters": total_cover_letters,
                "tone_breakdown": tone_breakdown,
                "average_word_count": round(avg_word_count, 1),
                "word_count_range": {
                    "min": min_words or 0,
                    "max": max_words or 0
                },
                "recent_activity": f"{recent_cover_letters} cover letters in the last 30 days",
                "top_companies": top_companies,
            }
            
            self.logger.debug("Generated cover letter statistics from database")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting cover letter stats: {e}", exc_info=True)
            return {
                "total_cover_letters": 0,
                "tone_breakdown": {},
                "recent_activity": "0 cover letters in the last 30 days",
                "error": str(e)
            }
    
    async def find_duplicates(self, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Find potential duplicate cover letters based on content similarity."""
        try:
            # For now, we'll do a simple approach by looking for exact job_title + company matches
            # In the future, this could be enhanced with semantic similarity
            stmt = select(
                DBCoverLetter.job_title,
                DBCoverLetter.company_name,
                func.count(DBCoverLetter.id).label('count')
            ).group_by(
                DBCoverLetter.job_title,
                DBCoverLetter.company_name
            ).having(func.count(DBCoverLetter.id) > 1)
            
            result = await self.session.execute(stmt)
            duplicates = []
            
            for job_title, company_name, count in result.all():
                # Get the actual cover letters for this combination
                detail_stmt = select(DBCoverLetter).where(
                    and_(
                        DBCoverLetter.job_title == job_title,
                        DBCoverLetter.company_name == company_name
                    )
                ).order_by(DBCoverLetter.created_at.desc())
                
                detail_result = await self.session.execute(detail_stmt)
                cover_letters = detail_result.scalars().all()
                
                duplicates.append({
                    "job_title": job_title,
                    "company_name": company_name,
                    "count": count,
                    "cover_letter_ids": [cl.id for cl in cover_letters]
                })
            
            self.logger.debug(f"Found {len(duplicates)} potential duplicate groups")
            return duplicates
            
        except Exception as e:
            self.logger.error(f"Error finding duplicate cover letters: {e}", exc_info=True)
            return []
