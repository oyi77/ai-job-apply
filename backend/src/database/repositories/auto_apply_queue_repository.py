"""Repository for auto-apply job queue."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DBAutoApplyJobQueue
from src.utils.logger import get_logger


class AutoApplyJobQueueRepository:
    """Repository for managing auto-apply job queue (external sites)."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository."""
        self.session = session
        self.logger = get_logger(__name__)

    async def add_to_queue(
        self, queue_item: DBAutoApplyJobQueue
    ) -> DBAutoApplyJobQueue:
        """Add a job to the queue.

        Args:
            queue_item: The queue item to add

        Returns:
            The created queue item
        """
        try:
            async with self.session.begin():
                self.session.add(queue_item)
                await self.session.flush()
                await self.session.refresh(queue_item)
            return queue_item
        except Exception as e:
            self.logger.error(f"Error adding to queue: {e}")
            raise

    async def get_queued_jobs(
        self, user_id: str, limit: int = 20, status: str = "pending"
    ) -> List[DBAutoApplyJobQueue]:
        """Get queued jobs for a user.

        Args:
            user_id: The user ID
            limit: Maximum number of jobs to return
            status: Filter by status (default: pending)

        Returns:
            List of queued jobs
        """
        try:
            stmt = (
                select(DBAutoApplyJobQueue)
                .where(
                    DBAutoApplyJobQueue.user_id == user_id,
                    DBAutoApplyJobQueue.status == status,
                )
                .order_by(DBAutoApplyJobQueue.created_at.desc())
                .limit(limit)
            )
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            self.logger.error(f"Error getting queued jobs: {e}")
            return []

    async def update_status(
        self, queue_id: str, status: str
    ) -> Optional[DBAutoApplyJobQueue]:
        """Update the status of a queued job.

        Args:
            queue_id: The queue ID
            status: New status

        Returns:
            The updated queue item or None if not found
        """
        try:
            async with self.session.begin():
                stmt = (
                    update(DBAutoApplyJobQueue)
                    .where(DBAutoApplyJobQueue.id == queue_id)
                    .values(status=status, updated_at=datetime.now(timezone.utc))
                    .returning(DBAutoApplyJobQueue)
                )
                result = await self.session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error updating queue status: {e}")
            raise

    async def get_by_id(self, queue_id: str) -> Optional[DBAutoApplyJobQueue]:
        """Get a queue item by ID.

        Args:
            queue_id: The queue ID

        Returns:
            The queue item or None if not found
        """
        try:
            stmt = select(DBAutoApplyJobQueue).where(DBAutoApplyJobQueue.id == queue_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting queue item: {e}")
            return None
