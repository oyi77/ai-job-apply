"""Integration tests for AutoApplyService activity logging."""

import json
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.database.config import Base
from src.database.models import DBAutoApplyConfig
from src.database.repositories.auto_apply_config_repository import (
    AutoApplyConfigRepository,
)
from src.database.repositories.auto_apply_activity_repository import (
    AutoApplyActivityLogRepository,
)
from src.services.auto_apply_service import AutoApplyService


@pytest.fixture
def mock_job_search_service():
    service = AsyncMock()
    service.search_jobs = AsyncMock(
        return_value=[
            {
                "id": "job1",
                "platform": "linkedin",
                "title": "Python Dev",
                "company": "Tech Corp",
            },
            {
                "id": "job2",
                "platform": "indeed",
                "title": "Backend Eng",
                "company": "Startup Inc",
            },
        ]
    )
    return service


@pytest.fixture
def mock_job_application_service():
    service = AsyncMock()
    service.apply = AsyncMock(return_value=True)
    return service


@pytest.fixture
def mock_ai_service():
    service = AsyncMock()
    return service


@pytest.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_run_cycle_creates_activity_log(
    db_session, mock_job_search_service, mock_job_application_service, mock_ai_service
):
    """Test that run_cycle creates an activity log entry."""
    # 1. Setup - Create user config
    user_id = f"test-user-{uuid.uuid4()}"
    config_repo = AutoApplyConfigRepository(db_session)

    config = DBAutoApplyConfig(
        user_id=user_id,
        enabled=True,
        search_criteria=json.dumps({"keywords": ["python"], "locations": ["remote"]}),
        platforms=json.dumps(["linkedin", "indeed"]),
        max_applications=10,
    )
    await config_repo.create(config)

    # 2. Setup - Create service
    # We mock database_config.get_session to return our test db_session
    # Since run_cycle uses its own session context manager, we need to patch it
    # or ensure it works with the test setup.
    # The integration tests usually use a real DB session.
    # But run_cycle does: async with database_config.get_session() as session:
    # We need to patch database_config.get_session to return an async context manager yielding db_session

    from src.database.config import database_config

    # Context manager mock
    class MockSessionContext:
        def __init__(self, session):
            self.session = session

        async def __aenter__(self):
            return self.session

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    original_get_session = database_config.get_session
    database_config.get_session = MagicMock(return_value=MockSessionContext(db_session))

    try:
        service = AutoApplyService(
            job_search_service=mock_job_search_service,
            job_application_service=mock_job_application_service,
            ai_service=mock_ai_service,
        )

        # 3. Execution
        await service.run_cycle()

        # Ensure any pending transactions are closed before verification
        if db_session.in_transaction():
            await db_session.commit()

        # Force refresh from DB
        db_session.expire_all()

        # 4. Verification
        # Check if activity log was created
        activity_repo = AutoApplyActivityLogRepository(db_session)
        logs = await activity_repo.get_user_activities(user_id)

        assert len(logs) > 0
        log = logs[0]
        assert log.user_id == user_id
        assert log.cycle_status == "completed"
        assert isinstance(log.cycle_start, datetime)
        assert log.cycle_start is not None
        assert log.jobs_searched == 2
        assert log.jobs_matched == 2
        # jobs_applied depends on rate limiter, which should allow 2 applications (default limits)
        # But we need to ensure rate limiter uses the same session
        assert log.jobs_applied == 2

    finally:
        # Cleanup
        database_config.get_session = original_get_session
