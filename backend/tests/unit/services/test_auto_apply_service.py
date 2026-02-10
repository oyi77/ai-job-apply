"""Unit tests for AutoApplyService workflow."""

import importlib
import json
from datetime import datetime, timezone
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import HttpUrl

from src.models.automation import AutoApplyConfig, AutoApplyConfigCreate
from src.models.job import Job, JobSearchResponse
from src.services.auto_apply_service import AutoApplyService, AutoApplyServiceProvider
from src.services.rate_limiter import RateLimitResult, RateLimiter

pytest = importlib.import_module("pytest")


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


def build_service(
    mock_session: AsyncMock,
    job_search_service: AsyncMock,
    job_application_service: AsyncMock,
    rate_limiter: AsyncMock,
    failure_logger: AsyncMock,
) -> AutoApplyService:
    return AutoApplyService(
        db_session=mock_session,
        job_search_service=job_search_service,
        job_application_service=job_application_service,
        ai_service=AsyncMock(),
        notification_service=AsyncMock(),
        session_manager=AsyncMock(),
        rate_limiter_factory=MagicMock(return_value=rate_limiter),
        failure_logger_factory=MagicMock(return_value=failure_logger),
    )


def create_db_config(
    user_id: str,
    enabled: bool = True,
    search_criteria: str | None = None,
    max_applications: int = 2,
) -> MagicMock:
    return MagicMock(
        id="config-1",
        user_id=user_id,
        enabled=enabled,
        search_criteria=search_criteria,
        platforms=None,
        max_applications=max_applications,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_or_update_config_creates_when_missing(
    mock_session: AsyncMock,
) -> None:
    config_data = AutoApplyConfigCreate(
        keywords=["python"],
        locations=["remote"],
        min_salary=100000,
        daily_limit=5,
    )
    db_config = create_db_config(
        "user-1",
        enabled=False,
        search_criteria=json.dumps(config_data.model_dump()),
        max_applications=5,
    )

    with patch("src.services.auto_apply_service.AutoApplyConfigRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.get_by_user_id = AsyncMock(return_value=None)
        repo.create = AsyncMock(return_value=db_config)

        service = AutoApplyService(db_session=mock_session)
        result = await service.create_or_update_config("user-1", config_data)

        repo.create.assert_called_once()
        assert isinstance(result, AutoApplyConfig)
        assert result.user_id == "user-1"
        assert result.daily_limit == 5


@pytest.mark.asyncio
async def test_create_or_update_config_updates_existing(
    mock_session: AsyncMock,
) -> None:
    config_data = AutoApplyConfigCreate(
        keywords=["data"],
        locations=["on-site"],
        min_salary=90000,
        daily_limit=3,
    )
    db_config = create_db_config("user-2")

    with patch("src.services.auto_apply_service.AutoApplyConfigRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.get_by_user_id = AsyncMock(return_value=db_config)
        repo.update = AsyncMock(return_value=db_config)

        service = AutoApplyService(db_session=mock_session)
        result = await service.create_or_update_config("user-2", config_data)

        repo.update.assert_called_once()
        assert result.user_id == "user-2"


@pytest.mark.asyncio
async def test_get_config_returns_none_when_missing(mock_session: AsyncMock) -> None:
    with patch("src.services.auto_apply_service.AutoApplyConfigRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.get_by_user_id = AsyncMock(return_value=None)
        service = AutoApplyService(db_session=mock_session)

        result = await service.get_config("user-3")

        assert result is None


@pytest.mark.asyncio
async def test_toggle_auto_apply_updates_enabled(mock_session: AsyncMock) -> None:
    with patch("src.services.auto_apply_service.AutoApplyConfigRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.update = AsyncMock()
        service = AutoApplyService(db_session=mock_session)

        await service.toggle_auto_apply("user-4", enabled=True)

        repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_get_activity_log_uses_repository(mock_session: AsyncMock) -> None:
    activity = MagicMock()
    with patch(
        "src.services.auto_apply_service.AutoApplyActivityLogRepository"
    ) as repo_cls:
        repo = repo_cls.return_value
        repo.get_user_activities = AsyncMock(return_value=[activity])
        service = AutoApplyService(db_session=mock_session)

        result = await service.get_activity_log("user-5", limit=10, offset=0)

        repo.get_user_activities.assert_called_once_with("user-5", limit=10, offset=0)
        assert result == [activity]


@pytest.mark.asyncio
async def test_update_rate_limits_uses_defaults(mock_session: AsyncMock) -> None:
    with patch("src.services.auto_apply_service.RateLimitRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.get_or_create = AsyncMock()
        service = AutoApplyService(db_session=mock_session)

        await service.update_rate_limits("user-6", platform="linkedin")

        defaults = RateLimiter.PLATFORM_LIMITS["linkedin"]
        repo.get_or_create.assert_called_once_with(
            "user-6",
            "linkedin",
            hourly_limit=defaults["hourly_limit"],
            daily_limit=defaults["daily_limit"],
        )


@pytest.mark.asyncio
async def test_get_external_site_queue_returns_dicts(mock_session: AsyncMock) -> None:
    queued_item = MagicMock(
        id="queue-1",
        job_id="job-1",
        platform="linkedin",
        status="queued",
        queued_at=datetime.now(timezone.utc),
        processed_at=None,
        error_message=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    with patch(
        "src.services.auto_apply_service.AutoApplyJobQueueRepository"
    ) as repo_cls:
        repo = repo_cls.return_value
        repo.get_queued_jobs = AsyncMock(return_value=[queued_item])
        service = AutoApplyService(db_session=mock_session)

        result = await service.get_external_site_queue("user-7", limit=5)

        repo.get_queued_jobs.assert_called_once_with("user-7", limit=5, status="queued")
        assert result[0]["job_id"] == "job-1"


@pytest.mark.asyncio
async def test_retry_queued_application_updates_status(mock_session: AsyncMock) -> None:
    queued_item = MagicMock(id="queue-2", job_id="job-2")
    with patch(
        "src.services.auto_apply_service.AutoApplyJobQueueRepository"
    ) as repo_cls:
        repo = repo_cls.return_value
        repo.get_queued_jobs = AsyncMock(return_value=[queued_item])
        repo.update_status = AsyncMock()
        service = AutoApplyService(db_session=mock_session)

        await service.retry_queued_application("user-8", "job-2")

        repo.update_status.assert_called_once_with("queue-2", "retry")


@pytest.mark.asyncio
async def test_skip_queued_application_updates_status(mock_session: AsyncMock) -> None:
    queued_item = MagicMock(id="queue-3", job_id="job-3")
    with patch(
        "src.services.auto_apply_service.AutoApplyJobQueueRepository"
    ) as repo_cls:
        repo = repo_cls.return_value
        repo.get_queued_jobs = AsyncMock(return_value=[queued_item])
        repo.update_status = AsyncMock()
        service = AutoApplyService(db_session=mock_session)

        await service.skip_queued_application("user-9", "job-3", "duplicate")

        repo.update_status.assert_called_once_with("queue-3", "skipped")


@pytest.mark.asyncio
async def test_run_cycle_enqueues_external_jobs_and_logs_activity(
    mock_session: AsyncMock,
) -> None:
    config = create_db_config(
        "user-10",
        search_criteria=json.dumps({"keywords": ["python"], "locations": ["remote"]}),
        max_applications=2,
    )
    external_job = Job(
        id="job-10",
        title="Backend Engineer",
        company="Example",
        location="Remote",
        url=cast(HttpUrl, "https://example.com/job-10"),
        portal="linkedin",
        description=None,
        salary=None,
        posted_date=None,
        experience_level=None,
        job_type=None,
        requirements=None,
        benefits=None,
        skills=None,
        external_application=True,
        apply_url=cast(HttpUrl, "https://external.example.com/apply"),
        contact_email=None,
        contact_phone=None,
        application_deadline=None,
    )
    response = JobSearchResponse(jobs={"linkedin": [external_job]}, total_jobs=1)

    job_search_service = AsyncMock()
    job_search_service.search_jobs = AsyncMock(return_value=response)
    job_application_service = AsyncMock()
    rate_limiter = AsyncMock()
    rate_limiter.can_apply = AsyncMock(return_value=RateLimitResult(allowed=True))
    failure_logger = AsyncMock()

    with (
        patch(
            "src.services.auto_apply_service.AutoApplyConfigRepository"
        ) as config_cls,
        patch(
            "src.services.auto_apply_service.AutoApplyActivityLogRepository"
        ) as activity_cls,
        patch(
            "src.services.auto_apply_service.AutoApplyJobQueueRepository"
        ) as queue_cls,
        patch("src.services.auto_apply_service.RateLimitRepository") as rate_cls,
    ):
        config_repo = config_cls.return_value
        activity_repo = activity_cls.return_value
        queue_repo = queue_cls.return_value
        rate_repo = rate_cls.return_value
        config_repo.get_active_configs = AsyncMock(return_value=[config])
        activity_repo.create = AsyncMock(return_value=MagicMock(id="log-1"))
        activity_repo.update_activity = AsyncMock()
        queue_repo.add_to_queue = AsyncMock()
        rate_repo.get_or_create = AsyncMock()

        service = build_service(
            mock_session,
            job_search_service,
            job_application_service,
            rate_limiter,
            failure_logger,
        )
        await service.run_cycle()

        queue_repo.add_to_queue.assert_called_once()
        job_application_service.apply_to_job.assert_not_called()


@pytest.mark.asyncio
async def test_run_cycle_updates_rate_limits_after_apply(
    mock_session: AsyncMock,
) -> None:
    config = create_db_config(
        "user-11",
        search_criteria=json.dumps({"keywords": ["python"], "locations": ["remote"]}),
        max_applications=1,
    )
    job = Job(
        id="job-11",
        title="Backend Engineer",
        company="Example",
        location="Remote",
        url=cast(HttpUrl, "https://example.com/job-11"),
        portal="linkedin",
        description=None,
        salary=None,
        posted_date=None,
        experience_level=None,
        job_type=None,
        requirements=None,
        benefits=None,
        skills=None,
        external_application=False,
        apply_url=None,
        contact_email=None,
        contact_phone=None,
        application_deadline=None,
    )
    response = JobSearchResponse(jobs={"linkedin": [job]}, total_jobs=1)

    job_search_service = AsyncMock()
    job_search_service.search_jobs = AsyncMock(return_value=response)
    job_application_service = AsyncMock()
    job_application_service.apply_to_job = AsyncMock(return_value={"success": True})
    rate_limiter = AsyncMock()
    rate_limiter.can_apply = AsyncMock(return_value=RateLimitResult(allowed=True))
    rate_limiter.record_application = AsyncMock()
    failure_logger = AsyncMock()

    with (
        patch(
            "src.services.auto_apply_service.AutoApplyConfigRepository"
        ) as config_cls,
        patch(
            "src.services.auto_apply_service.AutoApplyActivityLogRepository"
        ) as activity_cls,
        patch(
            "src.services.auto_apply_service.AutoApplyJobQueueRepository"
        ) as queue_cls,
        patch("src.services.auto_apply_service.RateLimitRepository") as rate_cls,
    ):
        config_repo = config_cls.return_value
        activity_repo = activity_cls.return_value
        rate_repo = rate_cls.return_value
        config_repo.get_active_configs = AsyncMock(return_value=[config])
        activity_repo.create = AsyncMock(return_value=MagicMock(id="log-2"))
        activity_repo.update_activity = AsyncMock()
        queue_cls.return_value.add_to_queue = AsyncMock()
        rate_repo.get_or_create = AsyncMock()
        rate_repo.update_count = AsyncMock(return_value=True)

        service = build_service(
            mock_session,
            job_search_service,
            job_application_service,
            rate_limiter,
            failure_logger,
        )
        await service.run_cycle()

        rate_limiter.record_application.assert_called_once_with("linkedin")
        rate_repo.update_count.assert_called_once_with("user-11", "linkedin")


@pytest.mark.asyncio
async def test_run_cycle_logs_failure_on_exception(mock_session: AsyncMock) -> None:
    config = create_db_config(
        "user-12",
        search_criteria=json.dumps({"keywords": ["python"], "locations": ["remote"]}),
        max_applications=1,
    )
    job_search_service = AsyncMock()
    job_search_service.search_jobs = AsyncMock(side_effect=RuntimeError("boom"))
    job_application_service = AsyncMock()
    rate_limiter = AsyncMock()
    failure_logger = AsyncMock()

    with (
        patch(
            "src.services.auto_apply_service.AutoApplyConfigRepository"
        ) as config_cls,
        patch(
            "src.services.auto_apply_service.AutoApplyActivityLogRepository"
        ) as activity_cls,
        patch(
            "src.services.auto_apply_service.AutoApplyJobQueueRepository"
        ) as queue_cls,
        patch("src.services.auto_apply_service.RateLimitRepository") as rate_cls,
    ):
        config_repo = config_cls.return_value
        activity_repo = activity_cls.return_value
        config_repo.get_active_configs = AsyncMock(return_value=[config])
        activity_repo.create = AsyncMock(return_value=MagicMock(id="log-3"))
        activity_repo.update_activity = AsyncMock()
        queue_cls.return_value.add_to_queue = AsyncMock()
        rate_cls.return_value.get_or_create = AsyncMock()

        service = build_service(
            mock_session,
            job_search_service,
            job_application_service,
            rate_limiter,
            failure_logger,
        )
        await service.run_cycle()

        failure_logger.log_error.assert_called_once()
        activity_repo.update_activity.assert_called_once()
