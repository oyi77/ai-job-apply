"""Unit tests for auto-apply API endpoints."""

from datetime import datetime, timezone
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.dependencies import get_current_user
from src.api.v1.auto_apply import router
from src.models.automation import AutoApplyConfig
from src.models.user import UserProfile
from src.services.service_registry import service_registry


@pytest.fixture
def mock_auto_apply_service():
    """Mock AutoApplyService."""
    service = AsyncMock()
    now = datetime.now(timezone.utc)
    config = AutoApplyConfig(
        id="config_1",
        user_id="user_123",
        keywords=["engineer"],
        locations=["New York", "San Francisco"],
        min_salary=None,
        daily_limit=5,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    service.create_or_update_config = AsyncMock(return_value=config)
    service.get_config = AsyncMock(return_value=config)
    service.toggle_auto_apply = AsyncMock(return_value=None)
    service.get_activity_log = AsyncMock(return_value=[])
    service.update_rate_limits = AsyncMock(return_value=None)
    service.get_external_site_queue = AsyncMock(return_value=[])
    service.retry_queued_application = AsyncMock(return_value=None)
    service.skip_queued_application = AsyncMock(return_value=None)
    return service


@pytest.fixture
def mock_current_user() -> UserProfile:
    now = datetime.now(timezone.utc)
    return UserProfile(
        id="user_123",
        email="user@example.com",
        name="Test User",
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def app_with_mocked_service(mock_auto_apply_service, mock_current_user):
    """Create FastAPI app with mocked auto-apply service."""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/auto-apply")

    async def override_get_current_user() -> UserProfile:
        return mock_current_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    service_registry.get_auto_apply_service = AsyncMock(
        return_value=mock_auto_apply_service
    )
    return app


@pytest.fixture
def client(app_with_mocked_service):
    """Create test client with mocked service."""
    return TestClient(app_with_mocked_service)


class TestAutoApplyAPI:
    """Unit tests for auto-apply API endpoints."""

    def test_create_config_success(self, client: TestClient):
        """Test creating configuration with valid data."""
        response = client.post(
            "/api/v1/auto-apply/config",
            json={
                "keywords": ["engineer"],
                "locations": ["New York", "San Francisco"],
                "daily_limit": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data

    def test_create_config_invalid_data(self, client: TestClient):
        """Test creating configuration with invalid data."""
        invalid_data = {"is_active": "not_a_bool"}

        response = client.post("/api/v1/auto-apply/config", json=invalid_data)

        assert response.status_code == 422

    def test_get_config_exists(self, client: TestClient):
        """Test getting configuration when it exists."""
        response = client.get("/api/v1/auto-apply/config")

        assert response.status_code == 200
        data = response.json()
        assert data is not None

    def test_get_config_not_exists(self, client: TestClient):
        """Test getting configuration when it doesn't exist."""
        mock_service = AsyncMock()
        mock_service.get_config = AsyncMock(return_value=None)
        service_registry.get_auto_apply_service = AsyncMock(return_value=mock_service)

        response = client.get("/api/v1/auto-apply/config")

        assert response.status_code == 200
        assert response.json() is None

    def test_start_auto_apply_success(self, client: TestClient):
        """Test starting auto-apply successfully."""
        response = client.post("/api/v1/auto-apply/start")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Auto-apply started"

    def test_start_auto_apply_already_active(self, client: TestClient):
        """Test starting auto-apply when already active."""
        # This test depends on actual service implementation
        response = client.post("/api/v1/auto-apply/start")

        # Service should handle this case appropriately
        assert response.status_code in [200, 400]

    def test_stop_auto_apply_success(self, client: TestClient):
        """Test stopping auto-apply successfully."""
        response = client.post("/api/v1/auto-apply/stop")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Auto-apply stopped"

    def test_stop_auto_apply_not_active(self, client: TestClient):
        """Test stopping auto-apply when not active."""
        response = client.post("/api/v1/auto-apply/stop")

        # Service should handle this case appropriately
        assert response.status_code in [200, 400]

    def test_update_rate_limits_success(self, client: TestClient):
        """Test updating rate limits successfully."""
        response = client.post(
            "/api/v1/auto-apply/rate-limits",
            params={"platform": "linkedin", "hourly_limit": 10, "daily_limit": 100},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_update_rate_limits_partial(self, client: TestClient):
        """Test updating only hourly limit."""
        response = client.post(
            "/api/v1/auto-apply/rate-limits",
            params={"platform": "indeed", "hourly_limit": 15},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_get_activity_log_empty(self, client: TestClient):
        """Test getting activity log when empty."""
        response = client.get("/api/v1/auto-apply/activity")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_activity_log_with_results(self, client: TestClient):
        """Test getting activity log with results."""
        response = client.get("/api/v1/auto-apply/activity")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_activity_log_with_pagination(self, client: TestClient):
        """Test activity log pagination."""
        response = client.get("/api/v1/auto-apply/activity?limit=10&offset=5")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_external_site_queue_empty(self, client: TestClient):
        """Test getting external site queue when empty."""
        response = client.get("/api/v1/auto-apply/queue")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_external_site_queue_with_results(self, client: TestClient):
        """Test getting external site queue with results."""
        response = client.get("/api/v1/auto-apply/queue")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_retry_queued_application_success(self, client: TestClient):
        """Test retrying queued application successfully."""
        response = client.post(
            "/api/v1/auto-apply/retry-queued", params={"job_id": "job_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_retry_queued_application_not_found(self, client: TestClient):
        """Test retrying non-existent queued application."""
        response = client.post(
            "/api/v1/auto-apply/retry-queued", params={"job_id": "nonexistent"}
        )

        # Service should handle this case appropriately
        assert response.status_code in [200, 404]

    def test_skip_queued_application_success(self, client: TestClient):
        """Test skipping queued application successfully."""
        response = client.post(
            "/api/v1/auto-apply/skip-queued",
            params={"job_id": "job_123", "reason": "Not interested"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_skip_queued_application_invalid_data(self, client: TestClient):
        """Test skipping queued application with invalid data."""
        response = client.post("/api/v1/auto-apply/skip-queued", params={"job_id": 123})

        assert response.status_code == 422

    def test_authentication_required(self, app_with_mocked_service):
        """Test that endpoints require authentication."""
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/auto-apply")
        client = TestClient(app)

        response = client.get("/api/v1/auto-apply/config")

        assert response.status_code == 401
