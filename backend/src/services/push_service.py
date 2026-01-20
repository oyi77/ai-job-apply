"""Web Push Notifications service.

Implements:
- Subscription management (subscribe/unsubscribe)
- Push sending via Web Push Protocol using pywebpush

This module avoids synchronous I/O inside async methods by offloading
pywebpush's blocking call to a worker thread.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import json
from typing import AsyncIterator, Callable, Optional

import anyio
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
from src.database.config import database_config
from src.database.repositories.push_subscription_repository import (
    PushSubscriptionRepository,
)
from src.models.push_subscription import PushMessage, PushSubscriptionCreate
from src.utils.logger import get_logger


SessionFactory = Callable[[], AsyncSession]


class PushService:
    """Service for managing and sending Web Push notifications."""

    def __init__(
        self,
        *,
        session_factory: Optional[SessionFactory] = None,
        vapid_private_key: Optional[str] = None,
        vapid_subject: Optional[str] = None,
        ttl: int = 60,
    ):
        self.logger = get_logger(__name__)
        self._session_factory = session_factory or database_config.get_session

        self._vapid_private_key = vapid_private_key or getattr(
            config, "vapid_private_key", None
        )
        self._vapid_subject = vapid_subject or getattr(
            config, "vapid_subject", "mailto:noreply@example.com"
        )
        self._ttl = ttl

        if not self._vapid_private_key:
            self.logger.warning(
                "VAPID private key not configured. Push sending will be disabled. "
                "Set VAPID_PRIVATE_KEY in environment/config."
            )

    @asynccontextmanager
    async def _session(self, session: Optional[AsyncSession]) -> AsyncIterator[AsyncSession]:
        if session is not None:
            yield session
            return

        async with self._session_factory() as created:
            yield created

    async def subscribe(
        self,
        *,
        user_id: str,
        subscription: PushSubscriptionCreate,
        session: Optional[AsyncSession] = None,
    ) -> str:
        """Create/update a subscription for a user.

        Returns:
            The subscription id.
        """

        async with self._session(session) as s:
            async with s.begin():
                repo = PushSubscriptionRepository(s)
                row = await repo.upsert(
                    user_id=user_id,
                    endpoint=subscription.endpoint,
                    p256dh_key=subscription.keys.p256dh,
                    auth_key=subscription.keys.auth,
                )

            # Ensure id is populated
            await s.refresh(row)
            return row.id

    async def unsubscribe(
        self,
        *,
        user_id: str,
        endpoint: str,
        session: Optional[AsyncSession] = None,
    ) -> bool:
        """Remove a subscription.

        Safety: only deletes the row if it belongs to the user.
        """

        async with self._session(session) as s:
            async with s.begin():
                repo = PushSubscriptionRepository(s)
                existing = await repo.get_by_endpoint(endpoint)
                if existing is None:
                    return False
                if existing.user_id != user_id:
                    return False
                deleted = await repo.delete_by_endpoint(endpoint)
                return deleted

    async def send_to_user(
        self,
        *,
        user_id: str,
        message: PushMessage,
        session: Optional[AsyncSession] = None,
    ) -> int:
        """Send a push notification to all subscriptions for a user.

        Returns:
            Number of attempted deliveries (0 means user unsubscribed / no subs).
        """

        if not self._vapid_private_key:
            self.logger.warning("Push send skipped: VAPID private key missing")
            return 0

        async with self._session(session) as s:
            repo = PushSubscriptionRepository(s)
            subs = await repo.list_by_user(user_id)
            if not subs:
                return 0

            payload = json.dumps(message.model_dump(exclude_none=True))
            attempted = 0
            for sub in subs:
                attempted += 1
                ok, should_delete = await self._send_webpush(
                    endpoint=sub.endpoint,
                    p256dh=sub.p256dh_key,
                    auth=sub.auth_key,
                    payload=payload,
                )
                if should_delete:
                    async with s.begin():
                        await repo.delete_by_endpoint(sub.endpoint)
            return attempted

    async def _send_webpush(
        self,
        *,
        endpoint: str,
        p256dh: str,
        auth: str,
        payload: str,
    ) -> tuple[bool, bool]:
        """Send a single Web Push message.

        Returns:
            (success, should_delete_subscription)
        """

        try:
            from pywebpush import webpush, WebPushException

            def _sync_send() -> None:
                webpush(
                    subscription_info={
                        "endpoint": endpoint,
                        "keys": {"p256dh": p256dh, "auth": auth},
                    },
                    data=payload,
                    vapid_private_key=self._vapid_private_key,
                    vapid_claims={"sub": self._vapid_subject},
                    ttl=self._ttl,
                )

            await anyio.to_thread.run_sync(_sync_send)
            return True, False

        except Exception as e:
            # pywebpush wraps HTTP errors in WebPushException
            should_delete = False
            try:
                from pywebpush import WebPushException

                if isinstance(e, WebPushException) and getattr(e, "response", None):
                    status = getattr(e.response, "status_code", None)
                    # 404/410: subscription is gone.
                    if status in (404, 410):
                        should_delete = True
            except Exception:
                # Best-effort; never fail the request because of error parsing.
                should_delete = False

            self.logger.warning(
                f"Web push send failed for endpoint={endpoint[:60]}...: {e}"
            )
            return False, should_delete
