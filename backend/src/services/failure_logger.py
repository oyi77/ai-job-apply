"""Failure Logger Service with Screenshot Capture.

Comprehensive error logging service that:
- Logs all errors with full context
- Captures screenshots for visual debugging evidence
- Stores errors and screenshots in database
- Provides structured logging for troubleshooting and monitoring
"""

import base64
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DBFailureLog
from src.utils.logger import get_logger


class FailureLoggerService:
    """Service for comprehensive failure logging with screenshot capture.

    Features:
    - Structured error logging with full context
    - Screenshot capture for visual debugging
    - Error categorization (network, form filling, AI service, etc.)
    - Job and application tracking
    - Database persistence for audit trail
    - Configurable log retention (default: 30 days)
    """

    def __init__(self, session: AsyncSession, user_id: str, retention_days: int = 30):
        """Initialize failure logger.

        Args:
            session: SQLAlchemy async session
            user_id: User ID for tracking
            retention_days: Number of days to retain logs (default: 30)
        """
        self.session = session
        self.user_id = user_id
        self.logger = get_logger(__name__)
        self.retention_days = retention_days
        self.screenshot_dir = "screenshots"  # Local directory for screenshots

    @asynccontextmanager
    async def _transaction(self) -> AsyncIterator[AsyncSession]:
        if self.session.in_transaction():
            yield self.session
        else:
            async with self.session.begin():
                yield self.session

    async def log_error(
        self,
        task_name: str,
        platform: str,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        screenshot: Optional[bytes] = None,
        job_id: Optional[str] = None,
        application_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an error with optional screenshot.

        Args:
            task_name: Name of the task that failed
            platform: Platform where error occurred (e.g., "linkedin", "indeed")
            error_type: Type of error (e.g., "network_error", "form_filling_error")
            error_message: Error message
            stack_trace: Stack trace if available
            screenshot: Binary image data (screenshot bytes)
            job_id: Associated job ID if applicable
            application_id: Associated application ID if applicable
        """
        try:
            # Encode screenshot to base64 if provided
            screenshot_b64 = None
            if screenshot:
                screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
                self.logger.debug(f"Screenshot captured, size: {len(screenshot)} bytes")

            db_log = DBFailureLog(
                id=str(uuid.uuid4()),
                user_id=self.user_id,
                task_name=task_name,
                platform=platform,
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                screenshot=screenshot_b64,
                job_id=job_id,
                application_id=application_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            # Persist to database
            async with self._transaction():
                self.session.add(db_log)
                await self.session.flush()  # Get ID

            log_extra = {
                "user_id": self.user_id,
                "platform": platform,
                "task_name": task_name,
                "job_id": job_id,
                "application_id": application_id,
                "failure_log_id": db_log.id,
            }
            if extra:
                log_extra.update(extra)

            self.logger.error(
                f"[{error_type}] {task_name} on {platform}: {error_message}",
                extra=log_extra,
            )

        except Exception as e:
            self.logger.error(f"Error logging failure: {e}", exc_info=True)

    async def log_form_filling_error(
        self,
        platform: str,
        field_name: str,
        error_message: str,
        screenshot: Optional[bytes] = None,
        job_id: Optional[str] = None,
        application_id: Optional[str] = None,
    ) -> None:
        """Log a form filling error with screenshot.

        Args:
            platform: Platform where form filling failed
            field_name: Name of the field that caused error
            error_message: Error message
            screenshot: Screenshot of the form with error
            job_id: Associated job ID if applicable
            application_id: Associated application ID if applicable
        """
        await self.log_error(
            task_name="form_filling",
            platform=platform,
            error_type="form_filling_error",
            error_message=error_message,
            screenshot=screenshot,
            job_id=job_id,
            application_id=application_id,
            extra={
                "field_name": field_name,
                "error_details": f"Failed to fill field '{field_name}'",
            },
        )

    async def log_network_error(
        self,
        platform: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        screenshot: Optional[bytes] = None,
        job_id: Optional[str] = None,
    ) -> None:
        """Log a network-related error.

        Args:
            platform: Platform where network error occurred
            error_message: Error message
            stack_trace: Stack trace if available
            screenshot: Screenshot of network error
            job_id: Associated job ID if applicable
        """
        await self.log_error(
            task_name="network_request",
            platform=platform,
            error_type="network_error",
            error_message=error_message,
            stack_trace=stack_trace,
            screenshot=screenshot,
            job_id=job_id,
            extra={
                "error_details": f"Network error on {platform}: {error_message}",
            },
        )

    async def log_ai_service_error(
        self,
        error_message: str,
        platform: Optional[str] = None,
        stack_trace: Optional[str] = None,
    ) -> None:
        """Log an AI service error.

        Args:
            error_message: Error message
            platform: Platform where AI service failed (optional)
            stack_trace: Stack trace if available
        """
        await self.log_error(
            task_name="ai_service",
            platform=platform or "internal",
            error_type="ai_service_error",
            error_message=error_message,
            stack_trace=stack_trace,
            screenshot=None,  # No screenshot for AI errors
            extra={
                "error_details": f"AI service error: {error_message}",
            },
        )

    async def log_rate_limit_error(
        self,
        platform: str,
        error_message: str,
        job_id: Optional[str] = None,
    ) -> None:
        """Log a rate limiting error.

        Args:
            platform: Platform where rate limit was hit
            error_message: Error message
            job_id: Associated job ID if applicable
        """
        await self.log_error(
            task_name="rate_limit",
            platform=platform,
            error_type="rate_limit_error",
            error_message=error_message,
            job_id=job_id,
            extra={
                "error_details": f"Rate limit reached on {platform}: {error_message}",
            },
        )

    async def get_failure_logs(
        self,
        user_id: Optional[str] = None,
        platform: Optional[str] = None,
        error_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Dict]:
        """Retrieve failure logs with filtering options.

        Args:
            user_id: User ID to filter by (optional)
            platform: Platform to filter by (optional)
            error_type: Error type to filter by (optional)
            limit: Maximum number of logs to return (default: 100)
            offset: Number of logs to skip (default: 0)

        Returns:
            List of failure logs matching filters
        """
        try:
            stmt = select(DBFailureLog)

            # Apply filters
            if user_id:
                stmt = stmt.where(DBFailureLog.user_id == user_id)
            if platform:
                stmt = stmt.where(DBFailureLog.platform == platform)
            if error_type:
                stmt = stmt.where(DBFailureLog.error_type == error_type)

            # Order by most recent first
            stmt = stmt.order_by(DBFailureLog.created_at.desc())

            # Apply pagination
            stmt = stmt.limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            logs = result.scalars().unique().all()

            # Convert to domain models
            return [log.to_dict() for log in logs]

        except Exception as e:
            self.logger.error(f"Error retrieving failure logs: {e}")
            return []

    async def cleanup_old_logs(self) -> int:
        """Clean up old failure logs beyond retention period.

        Returns:
            Number of logs deleted
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(
                days=self.retention_days
            )

            # Find logs older than cutoff
            stmt = select(DBFailureLog).where(DBFailureLog.created_at < cutoff_date)

            # Get count before deletion
            result = await self.session.execute(stmt)
            count = len(result.all())

            # Delete old logs
            async with self.session.begin():
                await self.session.execute(stmt)

            self.logger.info(
                f"Cleaned up {count} old failure logs (older than {self.retention_days} days)"
            )
            return count

        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}", exc_info=True)
            return 0

    async def get_error_statistics(
        self,
        user_id: str,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Get error statistics for a user.

        Args:
            user_id: User ID to get statistics for
            days: Number of days to analyze (default: 7)

        Returns:
            Dictionary with error counts by type and platform
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

            # Get all logs for user within time period
            stmt = (
                select(DBFailureLog)
                .where(DBFailureLog.user_id == user_id)
                .where(DBFailureLog.created_at >= cutoff_date)
            )

            result = await self.session.execute(stmt)
            logs = result.scalars().unique().all()

            # Calculate statistics
            stats = {
                "total_errors": len(logs),
                "by_error_type": {},
                "by_platform": {},
                "recent_errors": logs[:10],  # Last 10 errors
            }

            # Group by error type
            for log in logs:
                stats["by_error_type"][log.error_type] = (
                    stats["by_error_type"].get(log.error_type, 0) + 1
                )
                stats["by_platform"][log.platform] = (
                    stats["by_platform"].get(log.platform, 0) + 1
                )

            return stats

        except Exception as e:
            self.logger.error(f"Error calculating statistics: {e}")
            return {
                "total_errors": 0,
                "by_error_type": {},
                "by_platform": {},
                "recent_errors": [],
            }
