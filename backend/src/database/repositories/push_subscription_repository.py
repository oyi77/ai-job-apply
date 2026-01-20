"""Push subscription repository for database operations."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DBPushSubscription
from src.utils.logger import get_logger


class PushSubscriptionRepository:
    """Repository for Web Push subscription persistence."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = get_logger(__name__)

    async def upsert(
        self,
        *,
        user_id: str,
        endpoint: str,
        p256dh_key: str,
        auth_key: str,
    ) -> DBPushSubscription:
        """Create or update a subscription by endpoint."""

        stmt = select(DBPushSubscription).where(DBPushSubscription.endpoint == endpoint)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            existing.user_id = user_id
            existing.p256dh_key = p256dh_key
            existing.auth_key = auth_key
            await self.session.flush()
            return existing

        subscription = DBPushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh_key=p256dh_key,
            auth_key=auth_key,
        )
        self.session.add(subscription)
        await self.session.flush()
        return subscription

    async def list_by_user(self, user_id: str) -> List[DBPushSubscription]:
        """List all subscriptions for a user."""

        stmt = select(DBPushSubscription).where(DBPushSubscription.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_endpoint(self, endpoint: str) -> Optional[DBPushSubscription]:
        """Get a subscription by its endpoint."""

        stmt = select(DBPushSubscription).where(DBPushSubscription.endpoint == endpoint)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_endpoint(self, endpoint: str) -> bool:
        """Delete a subscription by endpoint."""

        stmt = delete(DBPushSubscription).where(DBPushSubscription.endpoint == endpoint)
        result = await self.session.execute(stmt)
        return bool(result.rowcount and result.rowcount > 0)
