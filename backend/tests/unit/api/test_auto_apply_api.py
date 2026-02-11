"""Unit tests for Auto-Apply API endpoints."""

from datetime import datetime, timezone
import sys
import types
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient


class _StubServiceRegistry:
    async def get_auth_service(self):
        raise RuntimeError("Auth service not configured for unit tests")


_service_registry_module = types.ModuleType("src.services.service_registry")
_service_registry_module.service_registry = _StubServiceRegistry()
sys.modules.setdefault("src.services.service_registry", _service_registry_module)

from src.api.dependencies import get_current_user  # noqa: E402
from src.api.v1.auto_apply import router as auto_apply_router  # noqa: E402
from src.models.automation import AutoApplyActivityLog, AutoApplyConfig  # noqa: E402
from src.models.user import UserProfile  # noqa: E402
from src.services.service_registry import service_registry  # noqa: E402


@pytest.fixture
def mock_current_user() -> UserProfile:
    """Mock current user for dependency injection."""
    return UserProfile(
        id="test-user-123",
        email="test@example.com",
        name="Test User",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_auto_apply_service(mock_current_user: UserProfile) -> AsyncMock:
    """Mock auto-apply service with expected behaviors."""
    service = AsyncMock()
    now = datetime.now(timezone.utc)

    config = AutoApplyConfig(
        id="config-123",
        user_id=mock_current_user.id,
        keywords=["Python", "FastAPI"],
        locations=["Remote"],
        min_salary=120000,
        daily_limit=5,
        is_active=False,
        created_at=now,
        updated_at=now,
    )

    activity = AutoApplyActivityLog(
        id="activity-123",
        user_id=mock_current_user.id,
        cycle_id="cycle-123",
        cycle_start=now,
        cycle_end=None,
        cycle_status="completed",
        jobs_searched=10,
        jobs_matched=4,
        jobs_applied=2,
        applications_successful=2,
        applications_failed=0,
        errors=None,
        screenshots=None,
        created_at=now,
        updated_at=now,
    )

    service.create_or_update_config = AsyncMock(return_value=config)
    service.get_config = AsyncMock(return_value=config)
    service.toggle_auto_apply = AsyncMock(return_value=True)
    service.update_rate_limits = AsyncMock(return_value=None)
    service.get_activity_log = AsyncMock(return_value=[activity])
    service.get_external_site_queue = AsyncMock(
        return_value=[{"job_id": "job-123", "platform": "linkedin"}]
    )
    service.retry_queued_application = AsyncMock(return_value=None)
    service.skip_queued_application = AsyncMock(return_value=None)

    return service


@pytest.fixture
def app_with_auth(mock_current_user: UserProfile):
    """Create FastAPI app with mocked authentication."""
    app = FastAPI()

    app.include_router(
        auto_apply_router, prefix="/api/v1/auto-apply", tags=["auto-apply"]
    )

    async def override_get_current_user() -> UserProfile:
        return mock_current_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    return app


@pytest.fixture
def client_authenticated(app_with_auth) -> TestClient:
    """Create authenticated test client."""
    return TestClient(app_with_auth)


@pytest.fixture
def client_unauthenticated() -> TestClient:
    """Create unauthenticated test client."""
    app = FastAPI()
    app.include_router(
        auto_apply_router, prefix="/api/v1/auto-apply", tags=["auto-apply"]
    )
    return TestClient(app)


class TestAutoApplyConfig:
    """Test cases for /config endpoint."""

    @pytest.mark.asyncio
    async def test_create_config_success(
        self, client_authenticated: TestClient, mock_auto_apply_service: AsyncMock
    ) -> None:
        """POST /config returns config payload."""
        with patch.object(
            service_registry,
            "get_auto_apply_service",
            new_callable=AsyncMock,
            return_value=mock_auto_apply_service,
            create=True,
        ):
            response = client_authenticated.post(
                "/api/v1/auto-apply/config",
                json={
                    "keywords": ["Python"],
                    "locations": ["Remote"],
                    "min_salary": 120000,
                    "daily_limit": 5,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "test-user-123"
            assert data["keywords"] == ["Python", "FastAPI"]

    @pytest.mark.asyncio
    async def test_create_config_validation_error(
        self, client_authenticated: TestClient
    ) -> None:
        """POST /config returns validation error for invalid payload."""
        response = client_authenticated.post(
            "/api/v1/auto-apply/config",
            json={
                "keywords": ["Python"],
                "locations": ["Remote"],
                "daily_limit": 100,
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_config_service_validation_error(
        self, client_authenticated: TestClient, mock_auto_apply_service: AsyncMock
    ) -> None:
        """POST /config returns 400 when service rejects payload."""
        mock_auto_apply_service.create_or_update_config = AsyncMock(
            side_effect=HTTPException(status_code=400, detail="Invalid config")
        )

        with patch.object(
            service_registry,
            "get_auto_apply_service",
            new_callable=AsyncMock,
            return_value=mock_auto_apply_service,
            create=True,
        ):
            response = client_authenticated.post(
                "/api/v1/auto-apply/config",
                json={
                    "keywords": ["Python"],
                    "locations": ["Remote"],
                    "daily_limit": 5,
                },
            )

            assert response.status_code == 400
            assert response.json()["detail"] == "Invalid config"

    @pytest.mark.asyncio
    async def test_get_config_success(
        self, client_authenticated: TestClient, mock_auto_apply_service: AsyncMock
    ) -> None:
        """GET /config returns current configuration."""
        with patch.object(
            service_registry,
            "get_auto_apply_service",
            new_callable=AsyncMock,
            return_value=mock_auto_apply_service,
            create=True,
        ):
            response = client_authenticated.get("/api/v1/auto-apply/config")

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "test-user-123"


class TestAutoApplyStartStop:
    """Test cases for /start and /stop endpoints."""

    @pytest.mark.asyncio
    async def test_start_auto_apply(
        self, client_authenticated: TestClient, mock_auto_apply_service: AsyncMock
    ) -> None:
        """POST /start toggles auto-apply on."""
        with patch.object(
            service_registry,
            "get_auto_apply_service",
            new_callable=AsyncMock,
            return_value=mock_auto_apply_service,
            create=True,
        ):
            response = client_authenticated.post("/api/v1/auto-apply/start")

            assert response.status_code == 200
            assert response.json()["message"] == "Auto-apply started"
            mock_auto_apply_service.toggle_auto_apply.assert_called_with(
                "test-user-123", enabled=True
            )

    @pytest.mark.asyncio
    async def test_stop_auto_apply(
        self, client_authenticated: TestClient, mock_auto_apply_service: AsyncMock
    ) -> None:
        """POST /stop toggles auto-apply off."""
        with patch.object(
            service_registry,
            "get_auto_apply_service",
            new_callable=AsyncMock,
            return_value=mock_auto_apply_service,
            create=True,
        ):
            response = client_authenticated.post("/api/v1/auto-apply/stop")

            assert response.status_code == 200
            assert response.json()["message"] == "Auto-apply stopped"
            mock_auto_apply_service.toggle_auto_apply.assert_called_with(
                "test-user-123", enabled=False
            )


class TestAutoApplyRateLimits:
    """Test cases for /rate-limits endpoint."""

    @pytest.mark.asyncio
    async def test_update_rate_limits_success(
        self, client_authenticated: TestClient, mock_auto_apply_service: AsyncMock
    ) -> None:
        """POST /rate-limits updates limits for a platform."""
        with patch.object(
            service_registry,
            "get_auto_apply_service",
            new_callable=AsyncMock,
            return_value=mock_auto_apply_service,
            create=True,
        ):
            response = client_authenticated.post(
                "/api/v1/auto-apply/rate-limits",
                params={
                    "platform": "linkedin",
                    "hourly_limit": 5,
                    "daily_limit": 10,
                },
            )

            assert response.status_code == 200
            assert response.json()["message"] == "Rate limits updated for linkedin"
            mock_auto_apply_service.update_rate_limits.assert_called_with(
                "test-user-123",
                platform="linkedin",
                hourly_limit=5,
                daily_limit=10,
            )

    @pytest.mark.asyncio
    async def test_update_rate_limits_validation_error(
        self, client_authenticated: TestClient
    ) -> None:
        """POST /rate-limits returns validation error without platform."""
        response = client_authenticated.post("/api/v1/auto-apply/rate-limits")

        assert response.status_code == 422


class TestAutoApplyActivityQueue:
    """Test cases for /activity and /queue endpoints."""

    @pytest.mark.asyncio
    async def test_get_activity_log(
        self, client_authenticated: TestClient, mock_auto_apply_service: AsyncMock
    ) -> None:
        """GET /activity returns activity list."""
        with patch.object(
            service_registry,
            "get_auto_apply_service",
            new_callable=AsyncMock,
            return_value=mock_auto_apply_service,
            create=True,
        ):
            response = client_authenticated.get(
                "/api/v1/auto-apply/activity", params={"limit": 10, "offset": 5}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            mock_auto_apply_service.get_activity_log.assert_called_with(
                "test-user-123", limit=10, offset=5
            )

    @pytest.mark.asyncio
    async def test_get_queue(
        self, client_authenticated: TestClient, mock_auto_apply_service: AsyncMock
    ) -> None:
        """GET /queue returns queued jobs."""
        with patch.object(
            service_registry,
            "get_auto_apply_service",
            new_callable=AsyncMock,
            return_value=mock_auto_apply_service,
            create=True,
        ):
            response = client_authenticated.get(
                "/api/v1/auto-apply/queue", params={"limit": 3}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            mock_auto_apply_service.get_external_site_queue.assert_called_with(
                "test-user-123", limit=3
            )

    @pytest.mark.asyncio
    async def test_retry_queued_application(
        self, client_authenticated: TestClient, mock_auto_apply_service: AsyncMock
    ) -> None:
        """POST /retry-queued triggers retry for job."""
        with patch.object(
            service_registry,
            "get_auto_apply_service",
            new_callable=AsyncMock,
            return_value=mock_auto_apply_service,
            create=True,
        ):
            response = client_authenticated.post(
                "/api/v1/auto-apply/retry-queued", params={"job_id": "job-123"}
            )

            assert response.status_code == 200
            assert response.json()["message"] == "Application job-123 queued for retry"
            mock_auto_apply_service.retry_queued_application.assert_called_with(
                "test-user-123", "job-123"
            )

    @pytest.mark.asyncio
    async def test_skip_queued_application(
        self, client_authenticated: TestClient, mock_auto_apply_service: AsyncMock
    ) -> None:
        """POST /skip-queued skips job with reason."""
        with patch.object(
            service_registry,
            "get_auto_apply_service",
            new_callable=AsyncMock,
            return_value=mock_auto_apply_service,
            create=True,
        ):
            response = client_authenticated.post(
                "/api/v1/auto-apply/skip-queued",
                params={"job_id": "job-123", "reason": "duplicate"},
            )

            assert response.status_code == 200
            assert (
                response.json()["message"] == "Application job-123 skipped: duplicate"
            )
            mock_auto_apply_service.skip_queued_application.assert_called_with(
                "test-user-123", "job-123", "duplicate"
            )


class TestAutoApplyAuthentication:
    """Test cases for auth requirements on auto-apply endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("method", "url", "params"),
        [
            ("post", "/api/v1/auto-apply/config", None),
            ("get", "/api/v1/auto-apply/config", None),
            ("post", "/api/v1/auto-apply/start", None),
            ("post", "/api/v1/auto-apply/stop", None),
            ("post", "/api/v1/auto-apply/rate-limits", {"platform": "linkedin"}),
            ("get", "/api/v1/auto-apply/activity", None),
            ("get", "/api/v1/auto-apply/queue", None),
            ("post", "/api/v1/auto-apply/retry-queued", {"job_id": "job-123"}),
            (
                "post",
                "/api/v1/auto-apply/skip-queued",
                {"job_id": "job-123", "reason": "duplicate"},
            ),
        ],
    )
    async def test_requires_authentication(
        self,
        client_unauthenticated: TestClient,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]],
    ) -> None:
        """Endpoints return 401 without authentication."""
        response = client_unauthenticated.request(method, url, params=params)

        assert response.status_code == 401
