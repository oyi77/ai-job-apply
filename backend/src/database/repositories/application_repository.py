"""Application repository for database operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload

from ..models import DBJobApplication, DBResume, DBCoverLetter
from ...models.application import JobApplication, ApplicationUpdateRequest, ApplicationStatus
from ...utils.logger import get_logger


class ApplicationRepository:
    """Repository for job application database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
        self.logger = get_logger(__name__)
    
    async def create(self, application: JobApplication) -> JobApplication:
        """Create a new job application."""
        try:
            db_application = DBJobApplication.from_model(application)
            self.session.add(db_application)
            await self.session.commit()
            await self.session.refresh(db_application)
            
            self.logger.info(f"Created application: {application.job_title} at {application.company}")
            return db_application.to_model()
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating application: {e}", exc_info=True)
            raise
    
    async def get_by_id(self, application_id: str) -> Optional[JobApplication]:
        """Get application by ID."""
        try:
            stmt = select(DBJobApplication).options(
                selectinload(DBJobApplication.resume),
                selectinload(DBJobApplication.cover_letter)
            ).where(DBJobApplication.id == application_id)
            
            result = await self.session.execute(stmt)
            db_application = result.scalar_one_or_none()
            
            if db_application:
                self.logger.debug(f"Retrieved application: {db_application.job_title}")
                return db_application.to_model()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting application {application_id}: {e}", exc_info=True)
            return None
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[JobApplication]:
        """Get all applications with optional pagination."""
        try:
            stmt = select(DBJobApplication).options(
                selectinload(DBJobApplication.resume),
                selectinload(DBJobApplication.cover_letter)
            ).order_by(DBJobApplication.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)
            
            result = await self.session.execute(stmt)
            db_applications = result.scalars().all()
            
            applications = [app.to_model() for app in db_applications]
            self.logger.debug(f"Retrieved {len(applications)} applications")
            
            return applications
            
        except Exception as e:
            self.logger.error(f"Error getting all applications: {e}", exc_info=True)
            return []
    
    async def get_by_status(self, status: ApplicationStatus, limit: Optional[int] = None) -> List[JobApplication]:
        """Get applications by status."""
        try:
            stmt = select(DBJobApplication).options(
                selectinload(DBJobApplication.resume),
                selectinload(DBJobApplication.cover_letter)
            ).where(DBJobApplication.status == status).order_by(DBJobApplication.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            db_applications = result.scalars().all()
            
            applications = [app.to_model() for app in db_applications]
            self.logger.debug(f"Retrieved {len(applications)} applications with status {status}")
            
            return applications
            
        except Exception as e:
            self.logger.error(f"Error getting applications by status {status}: {e}", exc_info=True)
            return []
    
    async def update(self, application_id: str, updates: ApplicationUpdateRequest) -> Optional[JobApplication]:
        """Update application."""
        try:
            # Get current application
            current_app = await self.get_by_id(application_id)
            if not current_app:
                self.logger.warning(f"Cannot update, application not found: {application_id}")
                return None
            
            # Prepare update data
            update_data = {}
            
            if updates.status is not None:
                update_data["status"] = updates.status
                # Auto-set applied_date when status changes to SUBMITTED
                if updates.status == ApplicationStatus.SUBMITTED and not current_app.applied_date:
                    update_data["applied_date"] = datetime.utcnow()
            
            if updates.notes is not None:
                update_data["notes"] = updates.notes
            
            if updates.follow_up_date is not None:
                update_data["follow_up_date"] = updates.follow_up_date
            
            if updates.interview_date is not None:
                update_data["interview_date"] = updates.interview_date
                # Auto-update status if interview is scheduled
                if current_app.status in [ApplicationStatus.SUBMITTED, ApplicationStatus.UNDER_REVIEW]:
                    update_data["status"] = ApplicationStatus.INTERVIEW_SCHEDULED
            
            update_data["updated_at"] = datetime.utcnow()
            
            # Perform update
            stmt = update(DBJobApplication).where(
                DBJobApplication.id == application_id
            ).values(**update_data)
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Return updated application
            updated_app = await self.get_by_id(application_id)
            self.logger.info(f"Updated application: {updated_app.job_title}")
            return updated_app
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating application {application_id}: {e}", exc_info=True)
            return None
    
    async def delete(self, application_id: str) -> bool:
        """Delete application."""
        try:
            stmt = delete(DBJobApplication).where(DBJobApplication.id == application_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                self.logger.info(f"Deleted application: {application_id}")
                return True
            
            self.logger.warning(f"Application not found for deletion: {application_id}")
            return False
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error deleting application {application_id}: {e}", exc_info=True)
            return False
    
    async def get_by_company(self, company: str, limit: Optional[int] = None) -> List[JobApplication]:
        """Get applications by company."""
        try:
            stmt = select(DBJobApplication).options(
                selectinload(DBJobApplication.resume),
                selectinload(DBJobApplication.cover_letter)
            ).where(
                func.lower(DBJobApplication.company) == company.lower()
            ).order_by(DBJobApplication.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            db_applications = result.scalars().all()
            
            applications = [app.to_model() for app in db_applications]
            self.logger.debug(f"Retrieved {len(applications)} applications for {company}")
            
            return applications
            
        except Exception as e:
            self.logger.error(f"Error getting applications for company {company}: {e}", exc_info=True)
            return []
    
    async def search(self, query: str, limit: Optional[int] = None) -> List[JobApplication]:
        """Search applications by job title, company, or notes."""
        try:
            search_term = f"%{query.lower()}%"
            
            stmt = select(DBJobApplication).options(
                selectinload(DBJobApplication.resume),
                selectinload(DBJobApplication.cover_letter)
            ).where(
                or_(
                    func.lower(DBJobApplication.job_title).like(search_term),
                    func.lower(DBJobApplication.company).like(search_term),
                    func.lower(DBJobApplication.notes).like(search_term)
                )
            ).order_by(DBJobApplication.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            db_applications = result.scalars().all()
            
            applications = [app.to_model() for app in db_applications]
            self.logger.debug(f"Found {len(applications)} applications matching '{query}'")
            
            return applications
            
        except Exception as e:
            self.logger.error(f"Error searching applications with query '{query}': {e}", exc_info=True)
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get application statistics."""
        try:
            # Get total count
            total_stmt = select(func.count(DBJobApplication.id))
            total_result = await self.session.execute(total_stmt)
            total_applications = total_result.scalar()
            
            # Get status breakdown
            status_stmt = select(
                DBJobApplication.status,
                func.count(DBJobApplication.id)
            ).group_by(DBJobApplication.status)
            
            status_result = await self.session.execute(status_stmt)
            status_breakdown = dict(status_result.all())
            
            # Ensure all statuses are represented
            for status in ApplicationStatus:
                if status not in status_breakdown:
                    status_breakdown[status] = 0
            
            # Calculate recent activity (last 30 days)
            recent_cutoff = datetime.utcnow() - timedelta(days=30)
            recent_stmt = select(func.count(DBJobApplication.id)).where(
                DBJobApplication.created_at >= recent_cutoff
            )
            recent_result = await self.session.execute(recent_stmt)
            recent_applications = recent_result.scalar()
            
            # Calculate success metrics
            successful_statuses = [
                ApplicationStatus.OFFER_RECEIVED,
                ApplicationStatus.OFFER_ACCEPTED,
                ApplicationStatus.INTERVIEW_COMPLETED
            ]
            
            successful_stmt = select(func.count(DBJobApplication.id)).where(
                DBJobApplication.status.in_(successful_statuses)
            )
            successful_result = await self.session.execute(successful_stmt)
            successful_apps = successful_result.scalar()
            
            # Calculate average response time
            response_time_stmt = select(
                func.avg(
                    func.extract('epoch', DBJobApplication.applied_date - DBJobApplication.created_at) / 86400
                )
            ).where(
                and_(
                    DBJobApplication.applied_date.is_not(None),
                    DBJobApplication.status != ApplicationStatus.DRAFT
                )
            )
            
            response_time_result = await self.session.execute(response_time_stmt)
            avg_response_time = response_time_result.scalar() or 0
            
            # Count pending interviews
            pending_interviews_stmt = select(func.count(DBJobApplication.id)).where(
                DBJobApplication.status == ApplicationStatus.INTERVIEW_SCHEDULED
            )
            pending_result = await self.session.execute(pending_interviews_stmt)
            pending_interviews = pending_result.scalar()
            
            # Count active applications
            active_statuses = [
                ApplicationStatus.SUBMITTED,
                ApplicationStatus.UNDER_REVIEW,
                ApplicationStatus.INTERVIEW_SCHEDULED,
                ApplicationStatus.INTERVIEW_COMPLETED
            ]
            
            active_stmt = select(func.count(DBJobApplication.id)).where(
                DBJobApplication.status.in_(active_statuses)
            )
            active_result = await self.session.execute(active_stmt)
            active_applications = active_result.scalar()
            
            stats = {
                "total_applications": total_applications,
                "status_breakdown": {status.value: count for status, count in status_breakdown.items()},
                "recent_activity": f"{recent_applications} applications in the last 30 days",
                "success_rate": (successful_apps / total_applications * 100) if total_applications > 0 else 0,
                "average_response_time_days": round(avg_response_time, 1),
                "pending_interviews": pending_interviews,
                "active_applications": active_applications,
            }
            
            self.logger.debug("Generated application statistics from database")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting application stats: {e}", exc_info=True)
            return {
                "total_applications": 0,
                "status_breakdown": {},
                "recent_activity": "0 applications in the last 30 days",
                "error": str(e)
            }
    
    async def get_upcoming_follow_ups(self, days_ahead: int = 7) -> List[JobApplication]:
        """Get applications with upcoming follow-ups."""
        try:
            cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            stmt = select(DBJobApplication).options(
                selectinload(DBJobApplication.resume),
                selectinload(DBJobApplication.cover_letter)
            ).where(
                and_(
                    DBJobApplication.follow_up_date.is_not(None),
                    DBJobApplication.follow_up_date <= cutoff_date
                )
            ).order_by(DBJobApplication.follow_up_date)
            
            result = await self.session.execute(stmt)
            db_applications = result.scalars().all()
            
            applications = [app.to_model() for app in db_applications]
            self.logger.debug(f"Retrieved {len(applications)} upcoming follow-ups")
            
            return applications
            
        except Exception as e:
            self.logger.error(f"Error getting upcoming follow-ups: {e}", exc_info=True)
            return []
