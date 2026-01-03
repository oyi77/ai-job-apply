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
from ...core.cache import cache_region
import time


class ApplicationRepository:
    """Repository for job application database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
        self.logger = get_logger(__name__)

    async def invalidate_statistics_cache(self, user_id: Optional[str] = None):
        """Invalidate the statistics cache."""
        try:
            cache_key = f"statistics:{user_id}"
            # dogpile.cache delete is synchronous, not async
            if cache_region is not None:
                cache_region.delete(cache_key)
                self.logger.debug(f"Invalidated statistics cache for user: {user_id}")
            else:
                self.logger.debug(f"Cache region not available, skipping invalidation for user: {user_id}")
        except Exception as e:
            # Don't fail the operation if cache invalidation fails
            self.logger.warning(f"Failed to invalidate cache for user {user_id}: {e}")
    
    async def create(self, application: JobApplication, user_id: Optional[str] = None) -> JobApplication:
        """Create a new job application, optionally associated with a user."""
        try:
            db_application = DBJobApplication.from_model(application)
            if user_id:
                db_application.user_id = user_id
            self.session.add(db_application)
            await self.session.commit()
            await self.session.refresh(db_application)
            
            self.logger.info(f"Created application: {application.job_title} at {application.company}")
            
            # Invalidate cache
            await self.invalidate_statistics_cache(user_id)
            
            return db_application.to_model()
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating application: {e}", exc_info=True)
            raise
    
    async def get_by_id(self, application_id: str, user_id: Optional[str] = None) -> Optional[JobApplication]:
        """Get application by ID, optionally filtered by user."""
        start_time = time.time()
        try:
            stmt = select(DBJobApplication).options(
                selectinload(DBJobApplication.resume),
                selectinload(DBJobApplication.cover_letter)
            ).where(DBJobApplication.id == application_id)
            
            # Filter by user_id if provided
            if user_id:
                stmt = stmt.where(DBJobApplication.user_id == user_id)
            
            result = await self.session.execute(stmt)
            db_application = result.scalar_one_or_none()
            
            elapsed_time = time.time() - start_time
            
            if db_application:
                self.logger.debug(
                    f"Retrieved application: {db_application.job_title} "
                    f"in {elapsed_time:.3f}s"
                )
                return db_application.to_model()
            
            return None
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(
                f"Error getting application {application_id} after {elapsed_time:.3f}s: {e}",
                exc_info=True
            )
            return None
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None, user_id: Optional[str] = None) -> List[JobApplication]:
        """Get all applications with optional pagination and user filtering."""
        start_time = time.time()
        try:
            stmt = select(DBJobApplication).options(
                selectinload(DBJobApplication.resume),
                selectinload(DBJobApplication.cover_letter)
            )
            
            # Filter by user_id if provided
            if user_id:
                stmt = stmt.where(DBJobApplication.user_id == user_id)
            
            stmt = stmt.order_by(DBJobApplication.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)
            
            result = await self.session.execute(stmt)
            db_applications = result.scalars().all()
            
            applications = [app.to_model() for app in db_applications]
            elapsed_time = time.time() - start_time
            
            self.logger.debug(
                f"Retrieved {len(applications)} applications in {elapsed_time:.3f}s"
            )
            
            # Log slow queries
            if elapsed_time > 0.1:  # 100ms threshold
                self.logger.warning(
                    f"Slow query: get_all took {elapsed_time:.3f}s "
                    f"(limit={limit}, offset={offset})"
                )
            
            return applications
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(
                f"Error getting all applications after {elapsed_time:.3f}s: {e}",
                exc_info=True
            )
            return []
    
    async def get_by_status(self, status: ApplicationStatus, limit: Optional[int] = None, user_id: Optional[str] = None) -> List[JobApplication]:
        """Get applications by status, optionally filtered by user."""
        try:
            stmt = select(DBJobApplication).options(
                selectinload(DBJobApplication.resume),
                selectinload(DBJobApplication.cover_letter)
            ).where(DBJobApplication.status == status)
            
            # Filter by user_id if provided
            if user_id:
                stmt = stmt.where(DBJobApplication.user_id == user_id)
            
            stmt = stmt.order_by(DBJobApplication.created_at.desc())
            
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
    
    async def update(self, application_id: str, updates: ApplicationUpdateRequest, user_id: Optional[str] = None) -> Optional[JobApplication]:
        """Update application, optionally filtered by user."""
        try:
            # Get current application (with user filter if provided)
            current_app = await self.get_by_id(application_id, user_id=user_id)
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
            
            # Perform update (with user filter if provided)
            where_clause = DBJobApplication.id == application_id
            if user_id:
                where_clause = and_(where_clause, DBJobApplication.user_id == user_id)
            
            stmt = update(DBJobApplication).where(where_clause).values(**update_data)
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Invalidate cache
            await self.invalidate_statistics_cache(user_id)
            
            # Return updated application
            updated_app = await self.get_by_id(application_id)
            self.logger.info(f"Updated application: {updated_app.job_title}")
            return updated_app
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating application {application_id}: {e}", exc_info=True)
            return None
    
    async def delete(self, application_id: str, user_id: Optional[str] = None) -> bool:
        """Delete application, optionally filtered by user."""
        try:
            where_clause = DBJobApplication.id == application_id
            if user_id:
                where_clause = and_(where_clause, DBJobApplication.user_id == user_id)
            
            stmt = delete(DBJobApplication).where(where_clause)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                self.logger.info(f"Deleted application: {application_id}")
                # Invalidate cache
                await self.invalidate_statistics_cache(user_id)
                return True
            
            self.logger.warning(f"Application not found for deletion: {application_id}")
            return False
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error deleting application {application_id}: {e}", exc_info=True)
            return False
    
    async def get_by_company(self, company: str, limit: Optional[int] = None) -> List[JobApplication]:
        """Get applications by company."""
        start_time = time.time()
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
            elapsed_time = time.time() - start_time
            
            self.logger.debug(
                f"Retrieved {len(applications)} applications for {company} "
                f"in {elapsed_time:.3f}s"
            )
            
            if elapsed_time > 0.1:
                self.logger.warning(
                    f"Slow query: get_by_company({company}) took {elapsed_time:.3f}s"
                )
            
            return applications
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(
                f"Error getting applications for company {company} after {elapsed_time:.3f}s: {e}",
                exc_info=True
            )
            return []
    
    async def search(self, query: str, limit: Optional[int] = None, user_id: Optional[str] = None) -> List[JobApplication]:
        """Search applications by job title, company, or notes, optionally filtered by user."""
        start_time = time.time()
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
            )
            
            # Filter by user_id if provided
            if user_id:
                stmt = stmt.where(DBJobApplication.user_id == user_id)
            
            stmt = stmt.order_by(DBJobApplication.created_at.desc())
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            db_applications = result.scalars().all()
            
            applications = [app.to_model() for app in db_applications]
            elapsed_time = time.time() - start_time
            
            self.logger.debug(
                f"Found {len(applications)} applications matching '{query}' "
                f"in {elapsed_time:.3f}s"
            )
            
            if elapsed_time > 0.1:
                self.logger.warning(
                    f"Slow query: search('{query}') took {elapsed_time:.3f}s"
                )
            
            return applications
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(
                f"Error searching applications with query '{query}' after {elapsed_time:.3f}s: {e}",
                exc_info=True
            )
            return []
    
    async def get_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get application statistics, optionally filtered by user."""
        start_time = time.time()
        try:
            # Base filter for user_id
            user_filter = DBJobApplication.user_id == user_id if user_id else None
            
            # Get total count
            total_stmt = select(func.count(DBJobApplication.id))
            if user_filter:
                total_stmt = total_stmt.where(user_filter)
            total_result = await self.session.execute(total_stmt)
            total_applications = total_result.scalar()
            
            # Get status breakdown
            status_stmt = select(
                DBJobApplication.status,
                func.count(DBJobApplication.id)
            ).group_by(DBJobApplication.status)
            if user_filter:
                status_stmt = status_stmt.where(user_filter)
            
            status_result = await self.session.execute(status_stmt)
            status_breakdown = dict(status_result.all())
            
            # Ensure all statuses are represented
            for status in ApplicationStatus:
                if status not in status_breakdown:
                    status_breakdown[status] = 0
            
            # Calculate recent activity (last 30 days)
            recent_cutoff = datetime.utcnow() - timedelta(days=30)
            recent_conditions = [DBJobApplication.created_at >= recent_cutoff]
            if user_filter:
                recent_conditions.append(user_filter)
            recent_stmt = select(func.count(DBJobApplication.id)).where(and_(*recent_conditions))
            recent_result = await self.session.execute(recent_stmt)
            recent_applications = recent_result.scalar()
            
            # Calculate success metrics
            successful_statuses = [
                ApplicationStatus.OFFER_RECEIVED,
                ApplicationStatus.OFFER_ACCEPTED,
                ApplicationStatus.INTERVIEW_COMPLETED
            ]
            
            successful_conditions = [DBJobApplication.status.in_(successful_statuses)]
            if user_filter:
                successful_conditions.append(user_filter)
            successful_stmt = select(func.count(DBJobApplication.id)).where(and_(*successful_conditions))
            successful_result = await self.session.execute(successful_stmt)
            successful_apps = successful_result.scalar()
            
            # Calculate average response time
            response_time_conditions = [
                DBJobApplication.applied_date.is_not(None),
                DBJobApplication.status != ApplicationStatus.DRAFT
            ]
            if user_filter:
                response_time_conditions.append(user_filter)
            response_time_stmt = select(
                func.avg(
                    func.extract('epoch', DBJobApplication.applied_date - DBJobApplication.created_at) / 86400
                )
            ).where(and_(*response_time_conditions))
            
            response_time_result = await self.session.execute(response_time_stmt)
            avg_response_time = response_time_result.scalar() or 0
            
            # Count pending interviews
            pending_conditions = [DBJobApplication.status == ApplicationStatus.INTERVIEW_SCHEDULED]
            if user_filter:
                pending_conditions.append(user_filter)
            pending_interviews_stmt = select(func.count(DBJobApplication.id)).where(and_(*pending_conditions))
            pending_result = await self.session.execute(pending_interviews_stmt)
            pending_interviews = pending_result.scalar()
            
            # Count active applications
            active_statuses = [
                ApplicationStatus.SUBMITTED,
                ApplicationStatus.UNDER_REVIEW,
                ApplicationStatus.INTERVIEW_SCHEDULED,
                ApplicationStatus.INTERVIEW_COMPLETED
            ]
            
            active_conditions = [DBJobApplication.status.in_(active_statuses)]
            if user_filter:
                active_conditions.append(user_filter)
            active_stmt = select(func.count(DBJobApplication.id)).where(and_(*active_conditions))
            active_result = await self.session.execute(active_stmt)
            active_applications = active_result.scalar()
            
            elapsed_time = time.time() - start_time
            
            stats = {
                "total_applications": total_applications,
                "status_breakdown": {status.value: count for status, count in status_breakdown.items()},
                "recent_activity": f"{recent_applications} applications in the last 30 days",
                "success_rate": (successful_apps / total_applications * 100) if total_applications > 0 else 0,
                "average_response_time_days": round(avg_response_time, 1),
                "pending_interviews": pending_interviews,
                "active_applications": active_applications,
            }
            
            self.logger.debug(
                f"Generated application statistics in {elapsed_time:.3f}s "
                f"(total: {total_applications})"
            )
            
            if elapsed_time > 0.1:
                self.logger.warning(
                    f"Slow query: get_statistics took {elapsed_time:.3f}s"
                )
            
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
        start_time = time.time()
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
            elapsed_time = time.time() - start_time
            
            self.logger.debug(
                f"Retrieved {len(applications)} upcoming follow-ups "
                f"in {elapsed_time:.3f}s"
            )
            
            if elapsed_time > 0.1:
                self.logger.warning(
                    f"Slow query: get_upcoming_follow_ups({days_ahead} days) "
                    f"took {elapsed_time:.3f}s"
                )
            
            return applications
            
        except Exception as e:
            self.logger.error(f"Error getting upcoming follow-ups: {e}", exc_info=True)
            return []
    async def bulk_create(self, applications: List[JobApplication], user_id: Optional[str] = None) -> List[JobApplication]:
        """Create multiple job applications."""
        try:
            db_applications = []
            for app in applications:
                db_app = DBJobApplication.from_model(app)
                if user_id:
                    db_app.user_id = user_id
                db_applications.append(db_app)
            
            self.session.add_all(db_applications)
            await self.session.commit()
            
            # Refresh all to get IDs and defaults
            for db_app in db_applications:
                await self.session.refresh(db_app)
            
            self.logger.info(f"Bulk created {len(applications)} applications")
            
            # Invalidate cache
            await self.invalidate_statistics_cache(user_id)
            
            return [db_app.to_model() for db_app in db_applications]
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error bulk creating applications: {e}", exc_info=True)
            raise

    async def bulk_update(self, application_ids: List[str], updates: ApplicationUpdateRequest, user_id: Optional[str] = None) -> List[JobApplication]:
        """Update multiple applications."""
        try:
            # Prepare update data
            update_data = {}
            if updates.status is not None:
                update_data["status"] = updates.status
                # Logic for auto-setting applied_date if becoming submitted is harder in bulk
                # We can use a CASE statement if needed, or just set it if null
                if updates.status == ApplicationStatus.SUBMITTED:
                     # Only set if currently null? standard update overrides.
                     # Let's use a conditional update for applied_date
                     # "applied_date": case([(DBJobApplication.applied_date.is_(None), func.now())], else_=DBJobApplication.applied_date)
                     # But simple approach:
                     pass
            
            if updates.notes is not None:
                update_data["notes"] = updates.notes
            
            if updates.follow_up_date is not None:
                update_data["follow_up_date"] = updates.follow_up_date
            
            if updates.interview_date is not None:
                update_data["interview_date"] = updates.interview_date
                if updates.status is None: # Auto-update status logic
                     # This effectively forces updating ID to INTERVIEW_SCHEDULED if it was submitted/under_view
                     # Complex to do purely in bulk update without reading first or complex SQL
                     pass

            update_data["updated_at"] = datetime.utcnow()
            
            # Construct where clause
            where_clause = DBJobApplication.id.in_(application_ids)
            if user_id:
                where_clause = and_(where_clause, DBJobApplication.user_id == user_id)
            
            # 1. Update status and basic fields
            stmt = update(DBJobApplication).where(where_clause).values(**update_data)
            
            # Handle conditional updates (applied_date, status change on interview)
            # For now, let's just do the basic update for efficiency. 
            # If we need complex logic, we might need to fetch-update-save or do custom SQL.
            # But the requirement is "Bulk Update Endpoint".
            # Let's explicitly handle the SUBMITTED case for applied_date using correlation/case if possible,
            # or just accept limitation.
            
            if updates.status == ApplicationStatus.SUBMITTED:
                 # Set applied_date to now if it is null
                 stmt = stmt.values(
                     applied_date=func.coalesce(DBJobApplication.applied_date, datetime.utcnow())
                 )

            await self.session.execute(stmt)
            await self.session.commit()
            
            # Invalidate cache
            await self.invalidate_statistics_cache(user_id)
            
            # Return updated items
            # Re-fetch them
            fetch_stmt = select(DBJobApplication).where(where_clause)
            result = await self.session.execute(fetch_stmt)
            db_apps = result.scalars().all()
            
            return [app.to_model() for app in db_apps]
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error bulk updating applications: {e}", exc_info=True)
            raise

    async def bulk_delete(self, application_ids: List[str], user_id: Optional[str] = None) -> bool:
        """Delete multiple applications."""
        try:
            where_clause = DBJobApplication.id.in_(application_ids)
            if user_id:
                where_clause = and_(where_clause, DBJobApplication.user_id == user_id)
            
            stmt = delete(DBJobApplication).where(where_clause)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            if result.rowcount > 0:
                self.logger.info(f"Bulk deleted {result.rowcount} applications")
                await self.invalidate_statistics_cache(user_id)
                return True
            
            return False
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error bulk deleting applications: {e}", exc_info=True)
            return False
