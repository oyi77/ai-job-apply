"""Unit tests for scheduler service."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from src.services.scheduler_service import ReminderConfig, SchedulerService  # noqa: E402


@pytest.fixture
def scheduler_service() -> SchedulerService:
    """Provide a scheduler service configured for immediate reminders."""
    config = ReminderConfig(
        follow_up_days=0,
        stale_application_days=0,
        check_interval_hours=1,
    )
    return SchedulerService(config=config)


@pytest.mark.asyncio
async def test_start_sets_running(scheduler_service: SchedulerService) -> None:
    """Scheduler start should set running state when initialized."""
    scheduler_service._initialized = True
    scheduler_service.scheduler = MagicMock()
    scheduler_service.scheduler.running = False

    started = await scheduler_service.start()

    assert started is True
    assert scheduler_service._running is True
    scheduler_service.scheduler.start.assert_called_once()


@pytest.mark.asyncio
async def test_schedule_follow_up_stores_job(
    scheduler_service: SchedulerService,
) -> None:
    """Scheduling a follow-up should store a reminder job."""
    application_date = datetime.now()

    job_id = await scheduler_service.schedule_follow_up(
        application_id="app-123",
        user_id="user-456",
        application_date=application_date,
        job_title="Software Engineer",
        company="ExampleCo",
    )

    assert job_id
    assert job_id in scheduler_service.reminder_jobs
    reminder = scheduler_service.reminder_jobs[job_id]
    assert reminder.reminder_type == "follow_up"
    assert reminder.metadata
    assert reminder.metadata["job_title"] == "Software Engineer"


@pytest.mark.asyncio
async def test_follow_up_metadata_override_triggers_immediate_send() -> None:
    """Metadata override should allow immediate follow-up execution."""
    service = SchedulerService(
        config=ReminderConfig(
            follow_up_days=7,
            stale_application_days=14,
            check_interval_hours=1,
        )
    )
    with patch(
        "src.services.notification_service.notification_service.send_follow_up_reminder",
        new=AsyncMock(return_value=True),
    ) as send_follow_up:
        job_id = await service.schedule_follow_up(
            application_id="app-override",
            user_id="user-override",
            application_date=datetime.now() - timedelta(seconds=1),
            job_title="Support Engineer",
            company="ExampleCo",
            metadata={"days_until_followup": 0},
        )

    send_follow_up.assert_called_once()
    assert service.reminder_jobs[job_id].sent is True


@pytest.mark.asyncio
async def test_check_reminders_sends_follow_up(
    scheduler_service: SchedulerService,
) -> None:
    """Due reminders should invoke the follow-up callback and mark sent."""
    application_date = datetime.now() - timedelta(days=1)

    job_id = await scheduler_service.schedule_follow_up(
        application_id="app-456",
        user_id="user-789",
        application_date=application_date,
        job_title="Backend Engineer",
        company="SampleCo",
    )

    with patch(
        "src.services.notification_service.notification_service.send_follow_up_reminder",
        new=AsyncMock(return_value=True),
    ) as send_follow_up:
        await scheduler_service._check_reminders()

    send_follow_up.assert_called_once()
    assert scheduler_service.reminder_jobs[job_id].sent is True
    assert scheduler_service.reminder_jobs[job_id].sent_at is not None


@pytest.mark.asyncio
async def test_follow_up_uses_metadata_email() -> None:
    """Follow-up reminder with past scheduled_time should be sent."""
    service = SchedulerService(
        config=ReminderConfig(
            follow_up_days=7,
            stale_application_days=14,
            check_interval_hours=1,
        )
    )
    with patch(
        "src.services.notification_service.notification_service.send_follow_up_reminder",
        new=AsyncMock(return_value=True),
    ) as send_follow_up:
        job_id = await service.schedule_follow_up(
            application_id="app-email",
            user_id="user-email",
            application_date=datetime.now() - timedelta(seconds=1),
            job_title="Backend Engineer",
            company="SampleCo",
            metadata={
                "days_until_followup": 0,
                "user_email": "tester@example.com",
                "user_name": "Tester",
            },
        )

    send_follow_up.assert_called_once()
    call_kwargs = send_follow_up.call_args.kwargs
    assert call_kwargs["user_email"] == "tester@example.com"
    assert call_kwargs["user_name"] == "Tester"

    job = service.reminder_jobs.get(job_id)
    assert job is not None
    assert job.sent is True


@pytest.mark.asyncio
async def test_schedule_follow_up_sends_immediately_when_due() -> None:
    """Scheduling a due follow-up should send immediately."""
    service = SchedulerService(
        config=ReminderConfig(
            follow_up_days=0,
            stale_application_days=14,
            check_interval_hours=1,
        )
    )
    application_date = datetime.now() - timedelta(seconds=1)

    with patch(
        "src.services.notification_service.notification_service.send_follow_up_reminder",
        new=AsyncMock(return_value=True),
    ) as send_follow_up:
        job_id = await service.schedule_follow_up(
            application_id="app-due",
            user_id="user-due",
            application_date=application_date,
            job_title="Backend Engineer",
            company="SampleCo",
            metadata={
                "days_until_followup": 0,
                "user_email": "tester@example.com",
                "user_name": "Tester",
            },
        )

    send_follow_up.assert_called_once()
    reminder = service.reminder_jobs[job_id]
    assert reminder.sent is True
    assert reminder.sent_at is not None


@pytest.mark.asyncio
async def test_cancel_reminder_removes_job(
    scheduler_service: SchedulerService,
) -> None:
    """Cancelling a reminder should remove it from storage."""
    application_date = datetime.now()

    job_id = await scheduler_service.schedule_follow_up(
        application_id="app-789",
        user_id="user-111",
        application_date=application_date,
        job_title="QA Engineer",
        company="QualityCo",
    )

    cancelled = await scheduler_service.cancel_reminder(job_id)

    assert cancelled is True
    assert job_id not in scheduler_service.reminder_jobs


@pytest.mark.asyncio
async def test_health_check_reflects_pending_reminders(
    scheduler_service: SchedulerService,
) -> None:
    """Health check should report pending reminders."""
    application_date = datetime.now()

    await scheduler_service.schedule_follow_up(
        application_id="app-999",
        user_id="user-222",
        application_date=application_date,
        job_title="DevOps Engineer",
        company="OpsCo",
    )

    health = await scheduler_service.health_check()

    assert health["pending_reminders"] == 1
