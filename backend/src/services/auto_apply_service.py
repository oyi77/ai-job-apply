"""Auto-apply service with full workflow implementation."""

from __future__ import annotations

import json
import traceback
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Callable, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import database_config
from src.database.models import DBAutoApplyConfig, DBAutoApplyJobQueue
from src.database.repositories.auto_apply_activity_repository import (
    AutoApplyActivityLogRepository,
)
from src.database.repositories.auto_apply_config_repository import (
    AutoApplyConfigRepository,
)
from src.database.repositories.auto_apply_queue_repository import (
    AutoApplyJobQueueRepository,
)
from src.database.repositories.rate_limit_repository import RateLimitRepository
from src.models.automation import (
    AutoApplyActivityLog,
    AutoApplyConfig,
    AutoApplyConfigCreate,
)
from src.models.job import Job, JobSearchRequest
from src.models.resume import Resume
from src.services.failure_logger import FailureLoggerService
from src.services.rate_limiter import RateLimiter
from src.utils.logger import get_logger


class AutoApplyServiceProvider:
    """Provider for AutoApplyService to enable per-user instances."""

    def __init__(
        self,
        job_search_service: Any = None,
        job_application_service: Any = None,
        ai_service: Any = None,
        notification_service: Any = None,
        session_manager: Any = None,
    ) -> None:
        self._job_search_service = job_search_service
        self._job_application_service = job_application_service
        self._ai_service = ai_service
        self._notification_service = notification_service
        self._session_manager = session_manager
        self._service: Optional[AutoApplyService] = None

    def get_service(self) -> "AutoApplyService":
        """Get the AutoApplyService instance."""
        if not self._service:
            raise RuntimeError("AutoApplyService not initialized")
        return self._service

    async def initialize(self) -> None:
        """Initialize the service instance with dependencies."""
        if not self._job_search_service or not self._job_application_service:
            try:
                from src.services.service_registry import service_registry

                instances = getattr(service_registry, "_instances", {})
                self._job_search_service = self._job_search_service or instances.get(
                    "job_search_service"
                )
                self._job_application_service = (
                    self._job_application_service
                    or instances.get("job_application_service")
                )
                self._ai_service = self._ai_service or instances.get("ai_service")
                self._notification_service = (
                    self._notification_service or instances.get("notification_service")
                )
            except Exception:
                pass

        self._service = AutoApplyService(
            job_search_service=self._job_search_service,
            job_application_service=self._job_application_service,
            ai_service=self._ai_service,
            notification_service=self._notification_service,
            session_manager=self._session_manager,
        )

    async def cleanup(self) -> None:
        """Clean up the service."""
        if self._service and hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class AutoApplyService:
    """Auto-apply service implementing the production workflow."""

    def __init__(
        self,
        job_search_service: Any = None,
        job_application_service: Any = None,
        ai_service: Any = None,
        notification_service: Any = None,
        session_manager: Any = None,
        db_session: Optional[AsyncSession] = None,
        session_provider: Optional[Callable[[], Any]] = None,
        rate_limiter_factory: Optional[
            Callable[[AsyncSession, str], RateLimiter]
        ] = None,
        failure_logger_factory: Optional[
            Callable[[AsyncSession, str], FailureLoggerService]
        ] = None,
    ) -> None:
        self.job_search_service = job_search_service
        self.job_application_service = job_application_service
        self.ai_service = ai_service
        self.notification_service = notification_service
        self.session_manager = session_manager
        self._db_session = db_session
        self._session_provider = session_provider or database_config.get_session
        self._rate_limiter_factory = rate_limiter_factory or (
            lambda session, user_id: RateLimiter(session, user_id)
        )
        self._failure_logger_factory = failure_logger_factory or (
            lambda session, user_id: FailureLoggerService(session, user_id)
        )
        self.logger = get_logger(__name__)

    @asynccontextmanager
    async def _get_session(self) -> AsyncIterator[AsyncSession]:
        if self._db_session is not None:
            yield self._db_session
        else:
            async with self._session_provider() as session:
                yield session

    async def create_or_update_config(
        self, user_id: str, config_data: AutoApplyConfigCreate
    ) -> AutoApplyConfig:
        async with self._get_session() as session:
            repo = AutoApplyConfigRepository(session)
            existing = await repo.get_by_user_id(user_id)
            search_criteria = json.dumps(
                {
                    "keywords": config_data.keywords,
                    "locations": config_data.locations,
                    "min_salary": config_data.min_salary,
                    "daily_limit": config_data.daily_limit,
                }
            )
            if existing:
                updated = await repo.update(
                    user_id,
                    {
                        "search_criteria": search_criteria,
                        "max_applications": config_data.daily_limit,
                        "updated_at": datetime.now(timezone.utc),
                    },
                )
                return self._to_config_model(updated)

            db_config = DBAutoApplyConfig(
                user_id=user_id,
                enabled=False,
                search_criteria=search_criteria,
                max_applications=config_data.daily_limit,
            )
            created = await repo.create(db_config)
            return self._to_config_model(created)

    async def get_config(self, user_id: str) -> Optional[AutoApplyConfig]:
        async with self._get_session() as session:
            repo = AutoApplyConfigRepository(session)
            db_config = await repo.get_by_user_id(user_id)
            if not db_config:
                return None
            return self._to_config_model(db_config)

    async def toggle_auto_apply(self, user_id: str, enabled: bool) -> None:
        async with self._get_session() as session:
            repo = AutoApplyConfigRepository(session)
            await repo.update(
                user_id,
                {"enabled": enabled, "updated_at": datetime.now(timezone.utc)},
            )

    async def cleanup(self) -> None:
        pass

    async def get_activity_log(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[AutoApplyActivityLog]:
        async with self._get_session() as session:
            activity_repo = AutoApplyActivityLogRepository(session)
            return await activity_repo.get_user_activities(
                user_id, limit=limit, offset=offset
            )

    async def update_rate_limits(
        self,
        user_id: str,
        platform: str,
        hourly_limit: Optional[int] = None,
        daily_limit: Optional[int] = None,
    ) -> None:
        defaults = RateLimiter.PLATFORM_LIMITS.get(platform)
        if not defaults:
            raise ValueError(f"Unsupported platform: {platform}")
        effective_hourly = hourly_limit or defaults["hourly_limit"]
        effective_daily = daily_limit or defaults["daily_limit"]
        async with self._get_session() as session:
            repo = RateLimitRepository(session)
            await repo.get_or_create(
                user_id,
                platform,
                hourly_limit=effective_hourly,
                daily_limit=effective_daily,
            )

    async def get_external_site_queue(
        self, user_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        async with self._get_session() as session:
            queue_repo = AutoApplyJobQueueRepository(session)
            queued = await queue_repo.get_queued_jobs(
                user_id, limit=limit, status="queued"
            )
            return [
                {
                    "id": item.id,
                    "job_id": item.job_id,
                    "platform": item.platform,
                    "status": item.status,
                    "queued_at": item.queued_at,
                    "processed_at": item.processed_at,
                    "error_message": item.error_message,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                }
                for item in queued
            ]

    async def retry_queued_application(self, user_id: str, job_id: str) -> None:
        async with self._get_session() as session:
            queue_repo = AutoApplyJobQueueRepository(session)
            queued = await queue_repo.get_queued_jobs(
                user_id, limit=100, status="queued"
            )
            if not queued:
                queued = await queue_repo.get_queued_jobs(
                    user_id, limit=100, status="failed"
                )
            match = next((item for item in queued if item.job_id == job_id), None)
            if match:
                await queue_repo.update_status(match.id, "retry")

    async def skip_queued_application(
        self, user_id: str, job_id: str, reason: str
    ) -> None:
        async with self._get_session() as session:
            queue_repo = AutoApplyJobQueueRepository(session)
            queued = await queue_repo.get_queued_jobs(
                user_id, limit=100, status="queued"
            )
            match = next((item for item in queued if item.job_id == job_id), None)
            if match:
                await queue_repo.update_status(match.id, "skipped")

    async def run_cycle(self) -> None:
        if not self.job_search_service or not self.job_application_service:
            raise RuntimeError("Auto-apply services not configured")

        async with self._get_session() as session:
            config_repo = AutoApplyConfigRepository(session)
            activity_repo = AutoApplyActivityLogRepository(session)
            queue_repo = AutoApplyJobQueueRepository(session)
            rate_repo = RateLimitRepository(session)

            configs = await config_repo.get_active_configs()
            if not configs:
                return

            for config in configs:
                cycle_id = str(uuid.uuid4())
                cycle_start = datetime.now(timezone.utc)
                activity = await activity_repo.create(
                    user_id=config.user_id,
                    cycle_id=cycle_id,
                    cycle_start=cycle_start,
                    cycle_status="running",
                )
                failure_logger = self._failure_logger_factory(session, config.user_id)
                rate_limiter = self._rate_limiter_factory(session, config.user_id)
                errors: List[Dict[str, Any]] = []
                screenshots: List[str] = []
                jobs_searched = 0
                jobs_matched = 0
                jobs_applied = 0
                applications_successful = 0
                applications_failed = 0
                try:
                    criteria = self._parse_search_criteria(config.search_criteria)
                    search_request = self._build_search_request(criteria, config)
                    response = await self.job_search_service.search_jobs(search_request)
                    total_jobs, jobs_by_platform = self._normalize_search_response(
                        response
                    )
                    jobs_searched = total_jobs
                    jobs_matched = total_jobs

                    applied_limit = config.max_applications
                    platform_limits_initialized: set[str] = set()
                    for platform, jobs in jobs_by_platform.items():
                        platform_key = platform or "unknown"
                        if platform_key not in platform_limits_initialized:
                            defaults = RateLimiter.PLATFORM_LIMITS.get(platform_key)
                            if defaults:
                                await rate_repo.get_or_create(
                                    config.user_id,
                                    platform_key,
                                    hourly_limit=defaults["hourly_limit"],
                                    daily_limit=defaults["daily_limit"],
                                )
                            platform_limits_initialized.add(platform_key)

                        for job in jobs:
                            if jobs_applied >= applied_limit:
                                break

                            can_apply = await rate_limiter.can_apply(platform_key)
                            if not can_apply.allowed:
                                await failure_logger.log_rate_limit_error(
                                    platform_key,
                                    "Rate limit reached",
                                    job_id=self._job_identifier(job),
                                )
                                errors.append(
                                    {
                                        "type": "rate_limit",
                                        "platform": platform_key,
                                        "job_id": self._job_identifier(job),
                                    }
                                )
                                continue

                            if self._is_external_job(job):
                                await queue_repo.add_to_queue(
                                    DBAutoApplyJobQueue(
                                        user_id=config.user_id,
                                        job_id=self._job_identifier(job),
                                        platform=platform_key,
                                        status="queued",
                                    )
                                )
                                continue

                            result = await self._apply_to_job(job, platform_key)
                            jobs_applied += 1
                            if result.get("success"):
                                applications_successful += 1
                                await rate_limiter.record_application(platform_key)
                                await rate_repo.update_count(
                                    config.user_id, platform_key
                                )
                            else:
                                applications_failed += 1
                                error_message = result.get(
                                    "error", "Application failed"
                                )
                                await failure_logger.log_error(
                                    task_name="apply_to_job",
                                    platform=platform_key,
                                    error_type="application_error",
                                    error_message=error_message,
                                    job_id=self._job_identifier(job),
                                )
                                errors.append(
                                    {
                                        "type": "application_error",
                                        "platform": platform_key,
                                        "job_id": self._job_identifier(job),
                                        "message": error_message,
                                    }
                                )

                    await activity_repo.update_activity(
                        activity.id,
                        cycle_end=datetime.now(timezone.utc),
                        cycle_status="completed",
                        jobs_searched=jobs_searched,
                        jobs_matched=jobs_matched,
                        jobs_applied=jobs_applied,
                        applications_successful=applications_successful,
                        applications_failed=applications_failed,
                        errors=json.dumps(errors) if errors else None,
                        screenshots=json.dumps(screenshots) if screenshots else None,
                    )
                except Exception as exc:
                    await failure_logger.log_error(
                        task_name="run_cycle",
                        platform="internal",
                        error_type="cycle_error",
                        error_message=str(exc),
                        stack_trace=traceback.format_exc(),
                    )
                    errors.append(
                        {
                            "type": "cycle_error",
                            "message": str(exc),
                        }
                    )
                    await activity_repo.update_activity(
                        activity.id,
                        cycle_end=datetime.now(timezone.utc),
                        cycle_status="failed",
                        jobs_searched=jobs_searched,
                        jobs_matched=jobs_matched,
                        jobs_applied=jobs_applied,
                        applications_successful=applications_successful,
                        applications_failed=applications_failed,
                        errors=json.dumps(errors) if errors else None,
                        screenshots=json.dumps(screenshots) if screenshots else None,
                    )

    async def _apply_to_job(self, job: Job, platform: str) -> Dict[str, Any]:
        resume = Resume(
            name="Auto Apply Resume",
            file_path="auto_apply_resume.pdf",
            file_type="pdf",
            content="",
            skills=None,
            experience_years=None,
            education=None,
            certifications=None,
            user_id=None,
        )
        return await self.job_application_service.apply_to_job(
            job=job,
            resume=resume,
            cover_letter="",
            additional_data={"source": "auto_apply", "platform": platform},
        )

    def _normalize_search_response(
        self, response: Any
    ) -> tuple[int, Dict[str, List[Any]]]:
        if hasattr(response, "jobs"):
            jobs_by_platform = response.jobs
            total_jobs = getattr(
                response,
                "total_jobs",
                sum(len(jobs) for jobs in jobs_by_platform.values()),
            )
            return total_jobs, jobs_by_platform

        if isinstance(response, list):
            jobs_by_platform: Dict[str, List[Any]] = {}
            for job in response:
                platform = "unknown"
                if isinstance(job, dict):
                    platform = job.get("platform") or "unknown"
                else:
                    platform = getattr(job, "platform", None) or "unknown"
                jobs_by_platform.setdefault(platform, []).append(job)
            return len(response), jobs_by_platform

        return 0, {}

    def _parse_search_criteria(self, raw: Optional[str]) -> Dict[str, Any]:
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    def _build_search_request(
        self, criteria: Dict[str, Any], config: DBAutoApplyConfig
    ) -> JobSearchRequest:
        keywords = criteria.get("keywords") or []
        locations = criteria.get("locations") or []
        min_salary = criteria.get("min_salary")
        location = locations[0] if locations else "Remote"
        platforms = self._parse_platforms(config.platforms)
        return JobSearchRequest(
            keywords=keywords,
            location=location,
            sites=platforms or None,
            results_wanted=config.max_applications,
            date_posted=None,
            salary_min=min_salary,
            salary_max=None,
            job_type=None,
        )

    def _parse_platforms(self, raw: Optional[str]) -> List[str]:
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
            return [str(item) for item in parsed] if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []

    def _is_external_job(self, job: Job | Dict[str, Any]) -> bool:
        if isinstance(job, dict):
            if job.get("external_application"):
                return True
            apply_url = job.get("apply_url")
            url = job.get("url")
            if apply_url and url and str(apply_url) != str(url):
                return True
            return False

        if job.external_application:
            return True
        if job.apply_url and str(job.apply_url) != str(job.url):
            return True
        return False

    def _job_identifier(self, job: Job | Dict[str, Any]) -> str:
        if isinstance(job, dict):
            return job.get("id") or job.get("url") or job.get("apply_url") or "unknown"

        return job.id or str(job.url)

    def _to_config_model(
        self, db_config: Optional[DBAutoApplyConfig]
    ) -> AutoApplyConfig:
        if not db_config:
            raise ValueError("Auto-apply configuration not found")
        criteria = self._parse_search_criteria(db_config.search_criteria)
        return AutoApplyConfig(
            id=db_config.id,
            user_id=db_config.user_id,
            keywords=criteria.get("keywords") or [],
            locations=criteria.get("locations") or [],
            min_salary=criteria.get("min_salary"),
            daily_limit=criteria.get("daily_limit") or db_config.max_applications,
            is_active=db_config.enabled,
            created_at=db_config.created_at,
            updated_at=db_config.updated_at,
        )
