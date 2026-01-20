"""Tests for Web Push notification service."""

from __future__ import annotations

import uuid
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.database.config import Base
from src.database.models import DBUser
from src.models.push_subscription import PushMessage, PushSubscriptionCreate
from src.services.push_service import PushService


@pytest.fixture
async def db_session_factory():
    """Create an isolated in-memory DB for push tests."""

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        yield factory
    finally:
        await engine.dispose()


@pytest.fixture
async def user_id(db_session_factory) -> str:
    """Create a user row and return its id."""

    uid = str(uuid.uuid4())
    async with db_session_factory() as session:
        async with session.begin():
            session.add(
                DBUser(
                    id=uid,
                    email=f"push_{uid}@example.com",
                    password_hash="hash",
                    name="Push User",
                )
            )
    return uid


@pytest.fixture
def push_service(db_session_factory) -> PushService:
    """Push service configured for tests."""

    return PushService(
        session_factory=db_session_factory,
        vapid_private_key="test-private-key",
        vapid_subject="mailto:test@example.com",
    )


def _sample_subscription() -> PushSubscriptionCreate:
    return PushSubscriptionCreate(
        endpoint="https://fcm.googleapis.com/fcm/send/test-token",
        keys={
            "p256dh": "p256dh-test",
            "auth": "auth-test",
        },
    )


@pytest.mark.asyncio
async def test_subscription_creation(push_service: PushService, user_id: str):
    subscription_id = await push_service.subscribe(
        user_id=user_id, subscription=_sample_subscription()
    )
    assert subscription_id


@pytest.mark.asyncio
async def test_push_notification_sending(push_service: PushService, user_id: str):
    await push_service.subscribe(user_id=user_id, subscription=_sample_subscription())

    with patch("src.services.push_service.anyio.to_thread.run_sync") as run_sync:
        run_sync.return_value = None

        attempted = await push_service.send_to_user(
            user_id=user_id,
            message=PushMessage(title="Hello", body="World", data={"x": 1}),
        )

    assert attempted == 1
    assert run_sync.called


@pytest.mark.asyncio
async def test_unsubscribe(push_service: PushService, user_id: str):
    sub = _sample_subscription()
    await push_service.subscribe(user_id=user_id, subscription=sub)

    removed = await push_service.unsubscribe(user_id=user_id, endpoint=sub.endpoint)
    assert removed is True


@pytest.mark.asyncio
async def test_no_push_to_unsubscribed_users(push_service: PushService, user_id: str):
    sub = _sample_subscription()
    await push_service.subscribe(user_id=user_id, subscription=sub)
    await push_service.unsubscribe(user_id=user_id, endpoint=sub.endpoint)

    with patch("src.services.push_service.anyio.to_thread.run_sync") as run_sync:
        run_sync.return_value = None

        attempted = await push_service.send_to_user(
            user_id=user_id,
            message=PushMessage(title="Hello", body="World"),
        )

    assert attempted == 0
    assert run_sync.called is False
