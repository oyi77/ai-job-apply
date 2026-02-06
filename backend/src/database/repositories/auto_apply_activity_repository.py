"""Repository for AutoApply Activity Log operations."""

import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator, List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DBAutoApplyActivityLog
from src.models.automation import AutoApplyActivityLog


class AutoApplyActivityLogRepository:
    """Repository for managing auto-apply activity logs."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    @asynccontextmanager
    async def _transaction(self) -> AsyncIterator[AsyncSession]:
        if self.session.in_transaction():
            yield self.session
        else:
            async with self.session.begin():
                yield self.session

    async def create(
        self,
        user_id: str,
        cycle_id: Optional[str] = None,
        cycle_start: Optional[datetime] = None,
        cycle_status: str = "pending",
        jobs_searched: int = 0,
        jobs_matched: int = 0,
        jobs_applied: int = 0,
        errors: Optional[str] = None,
        screenshots: Optional[str] = None,
    ) -> AutoApplyActivityLog:
        """Create a new activity log entry.

        Args:
            user_id: User ID for this activity log
            cycle_id: Optional cycle identifier
            cycle_start: Optional cycle start timestamp
            cycle_status: Status of the cycle (pending, running, completed, failed)
            jobs_searched: Number of jobs searched
            jobs_matched: Number of jobs matched
            jobs_applied: Number of jobs applied
            errors: Optional JSON string of error details
            screenshots: Optional JSON string of screenshot paths

        Returns:
            Created AutoApplyActivityLog instance
        """
        async with self._transaction():
            db_log = DBAutoApplyActivityLog(
                id=str(uuid.uuid4()),
                user_id=user_id,
                cycle_id=cycle_id,
                cycle_start=cycle_start or datetime.now(timezone.utc),
                cycle_status=cycle_status,
                jobs_searched=jobs_searched,
                jobs_matched=jobs_matched,
                jobs_applied=jobs_applied,
                applications_successful=0,
                applications_failed=0,
                errors=errors,
                screenshots=screenshots,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.session.add(db_log)

        return self._to_model(db_log)

    async def get_by_id(self, log_id: str) -> Optional[AutoApplyActivityLog]:
        """Get activity log by ID.

        Args:
            log_id: Activity log ID

        Returns:
            AutoApplyActivityLog if found, None otherwise
        """
        async with self._transaction():
            result = await self.session.execute(
                select(DBAutoApplyActivityLog).where(
                    DBAutoApplyActivityLog.id == log_id
                )
            )
            db_log = result.scalar_one_or_none()

        return self._to_model(db_log) if db_log else None

    async def get_user_activities(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        cycle_status: Optional[str] = None,
    ) -> List[AutoApplyActivityLog]:
        """Get paginated activity logs for a user.

        Args:
            user_id: User ID
            limit: Maximum number of results (default 20)
            offset: Number of results to skip (default 0)
            cycle_status: Optional status filter

        Returns:
            List of AutoApplyActivityLog instances
        """
        async with self._transaction():
            conditions = [DBAutoApplyActivityLog.user_id == user_id]

            if cycle_status:
                conditions.append(DBAutoApplyActivityLog.cycle_status == cycle_status)

            # Get paginated results
            result = await self.session.execute(
                select(DBAutoApplyActivityLog)
                .where(and_(*conditions))
                .order_by(DBAutoApplyActivityLog.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            db_logs = result.scalars().all()

        return [self._to_model(db_log) for db_log in db_logs]

    async def get_latest_cycle(self, user_id: str) -> Optional[AutoApplyActivityLog]:
        """Get the most recent cycle for a user.

        Args:
            user_id: User ID

        Returns:
            Most recent AutoApplyActivityLog if found, None otherwise
        """
        async with self._transaction():
            result = await self.session.execute(
                select(DBAutoApplyActivityLog)
                .where(DBAutoApplyActivityLog.user_id == user_id)
                .order_by(DBAutoApplyActivityLog.created_at.desc())
                .limit(1)
            )
            db_log = result.scalar_one_or_none()

        return self._to_model(db_log) if db_log else None

    async def get_cycles_in_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
    ) -> List[AutoApplyActivityLog]:
        """Get activity logs within a date range for a user.

        Args:
            user_id: User ID
            start_date: Start of date range
            end_date: End of date range
            limit: Maximum number of results (default 100)

        Returns:
            List of AutoApplyActivityLog instances within the date range
        """
        async with self._transaction():
            result = await self.session.execute(
                select(DBAutoApplyActivityLog)
                .where(
                    and_(
                        DBAutoApplyActivityLog.user_id == user_id,
                        DBAutoApplyActivityLog.created_at >= start_date,
                        DBAutoApplyActivityLog.created_at <= end_date,
                    )
                )
                .order_by(DBAutoApplyActivityLog.created_at.desc())
                .limit(limit)
            )
            db_logs = result.scalars().all()

        return [self._to_model(db_log) for db_log in db_logs]

    async def update_activity(
        self,
        log_id: str,
        cycle_end: Optional[datetime] = None,
        cycle_status: Optional[str] = None,
        jobs_searched: Optional[int] = None,
        jobs_matched: Optional[int] = None,
        jobs_applied: Optional[int] = None,
        applications_successful: Optional[int] = None,
        applications_failed: Optional[int] = None,
        errors: Optional[str] = None,
        screenshots: Optional[str] = None,
    ) -> Optional[AutoApplyActivityLog]:
        """Update an activity log with results.

        Args:
            log_id: Activity log ID
            cycle_end: Optional cycle end timestamp
            cycle_status: Optional updated status
            jobs_searched: Optional updated jobs searched count
            jobs_matched: Optional updated jobs matched count
            jobs_applied: Optional updated jobs applied count
            applications_successful: Optional successful applications count
            applications_failed: Optional failed applications count
            errors: Optional JSON string of error details
            screenshots: Optional JSON string of screenshot paths

        Returns:
            Updated AutoApplyActivityLog if found, None otherwise
        """
        async with self._transaction():
            result = await self.session.execute(
                select(DBAutoApplyActivityLog).where(
                    DBAutoApplyActivityLog.id == log_id
                )
            )
            db_log = result.scalar_one_or_none()

            if not db_log:
                return None

            # Update fields if provided
            if cycle_end is not None:
                db_log.cycle_end = cycle_end
            if cycle_status is not None:
                db_log.cycle_status = cycle_status
            if jobs_searched is not None:
                db_log.jobs_searched = jobs_searched
            if jobs_matched is not None:
                db_log.jobs_matched = jobs_matched
            if jobs_applied is not None:
                db_log.jobs_applied = jobs_applied
            if applications_successful is not None:
                db_log.applications_successful = applications_successful
            if applications_failed is not None:
                db_log.applications_failed = applications_failed
            if errors is not None:
                db_log.errors = errors
            if screenshots is not None:
                db_log.screenshots = screenshots

            db_log.updated_at = datetime.now(timezone.utc)

        return self._to_model(db_log)

    async def delete(self, log_id: str) -> bool:
        """Delete an activity log.

        Args:
            log_id: Activity log ID

        Returns:
            True if deleted, False if not found
        """
        async with self._transaction():
            result = await self.session.execute(
                select(DBAutoApplyActivityLog).where(
                    DBAutoApplyActivityLog.id == log_id
                )
            )
            db_log = result.scalar_one_or_none()

            if not db_log:
                return False

            await self.session.delete(db_log)

        return True

    def _to_model(self, db_log: DBAutoApplyActivityLog) -> AutoApplyActivityLog:
        """Convert database model to domain model.

        Args:
            db_log: Database model instance

        Returns:
            AutoApplyActivityLog domain model
        """
        return AutoApplyActivityLog(
            id=db_log.id,
            user_id=db_log.user_id,
            cycle_id=db_log.cycle_id,
            cycle_start=db_log.cycle_start,
            cycle_end=db_log.cycle_end,
            cycle_status=db_log.cycle_status,
            jobs_searched=db_log.jobs_searched,
            jobs_matched=db_log.jobs_matched,
            jobs_applied=db_log.jobs_applied,
            applications_successful=db_log.applications_successful,
            applications_failed=db_log.applications_failed,
            errors=db_log.errors,
            screenshots=db_log.screenshots,
            created_at=db_log.created_at,
            updated_at=db_log.updated_at,
        )
