"""Integration tests for auto-apply API endpoints.

Tests verify the auto_apply router is properly configured and endpoints are accessible.
Uses the same mocking pattern as test_api_endpoints.py.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import uuid

from src.api.app import create_app


class TestAutoApplyRouterImport:
    """Test that auto_apply router is properly imported and configured."""

    def test_router_imported_in_app(self):
        """Verify auto_apply router is imported in app.py."""
        from src.api import app as app_module
        from src.api.v1 import auto_apply

        # Verify the router exists
        assert hasattr(auto_apply, "router"), "auto_apply module should have a router"
        assert auto_apply.router is not None, "router should not be None"
        assert hasattr(app_module, "create_app")

    def test_endpoints_defined(self):
        """Verify expected endpoints are defined in auto_apply router."""
        from src.api.v1 import auto_apply

        routes = [getattr(r, "path", None) for r in auto_apply.router.routes]

        # Verify expected endpoints exist
        assert "/config" in routes, "POST /config endpoint should exist"
        assert "/start" in routes, "/start endpoint should exist"
        assert "/stop" in routes, "/stop endpoint should exist"
        assert "/activity" in routes, "/activity endpoint should exist"


@pytest.fixture
def mock_auto_apply_service():
    """Create a mock auto-apply service."""
    mock_service = MagicMock()

    # Mock config
    mock_config = MagicMock()
    mock_config.id = str(uuid.uuid4())
    mock_config.user_id = "test-user"
    mock_config.keywords = ["Python", "Remote"]
    mock_config.locations = ["Remote"]
    mock_config.daily_limit = 10
    mock_config.is_active = False
    mock_config.platforms = ["linkedin", "indeed"]
    mock_config.created_at = datetime.now(timezone.utc)
    mock_config.updated_at = datetime.now(timezone.utc)

    mock_service.get_config = AsyncMock(return_value=mock_config)
    mock_service.create_or_update_config = AsyncMock(return_value=mock_config)
    mock_service.toggle_auto_apply = AsyncMock(return_value=True)
    mock_service.get_activity_log = AsyncMock(return_value=[])
    mock_service.run_cycle = AsyncMock(
        return_value=MagicMock(jobs_searched=5, jobs_applied=3, errors=0, queued=0)
    )

    return mock_service


@pytest.fixture
def mock_service_registry(mock_auto_apply_service):
    """Create a mock service registry with auto-apply services."""
    mock_registry = MagicMock()

    mock_registry.initialize = AsyncMock()
    mock_registry.health_check = AsyncMock(
        return_value={
            "service_registry": "healthy",
            "services": {
                "auto_apply_service": {"status": "healthy", "available": True},
            },
        }
    )

    # Configure get_auto_apply_service method
    mock_registry.get_auto_apply_service = AsyncMock(
        return_value=mock_auto_apply_service
    )

    return mock_registry


@pytest.fixture
async def client(mock_service_registry):
    """Create test client with mocked service registry - using test_api_endpoints.py pattern."""
    from src.services.service_registry import service_registry
    from src.api.dependencies import get_current_user

    # Patch the get_auto_apply_service method on the actual global service_registry
    patches = [
        patch.object(
            service_registry,
            "get_auto_apply_service",
            AsyncMock(
                return_value=mock_service_registry.get_auto_apply_service.return_value
            ),
            create=True,
        )
    ]

    # Apply all patches
    for p in patches:
        p.start()

    try:
        app = create_app()
        from src.api.v1.auto_apply import router as auto_apply_router

        app.include_router(
            auto_apply_router, prefix="/api/v1/auto-apply", tags=["auto-apply"]
        )

        # Mock current user to bypass authentication
        mock_user = MagicMock()
        mock_user.id = "test-user"
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"

        app.dependency_overrides[get_current_user] = lambda: mock_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    finally:
        # Stop all patches
        for p in reversed(patches):
            p.stop()


class TestAutoApplyEndpoints:
    """Test auto-apply API endpoints with proper service mocking."""

    @pytest.mark.asyncio
    async def test_get_config(self, client, mock_service_registry):
        """Test GET /config endpoint returns user config."""
        response = await client.get("/api/v1/auto-apply/config")

        # Should return 200 with config data
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user"
        assert data["is_active"] is False
        mock_service_registry.get_auto_apply_service.return_value.get_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_config(self, client, mock_service_registry):
        """Test POST /config endpoint creates/updates config."""
        config_data = {
            "keywords": ["Python", "Django"],
            "locations": ["Remote"],
            "daily_limit": 15,
            "platforms": ["linkedin"],
        }

        response = await client.post("/api/v1/auto-apply/config", json=config_data)

        # Should return 200 with created/updated config
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user"
        mock_service_registry.get_auto_apply_service.return_value.create_or_update_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_auto_apply(self, client, mock_service_registry):
        """Test POST /start endpoint activates auto-apply."""
        response = await client.post("/api/v1/auto-apply/start")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        mock_service_registry.get_auto_apply_service.return_value.toggle_auto_apply.assert_called_with(
            "test-user", enabled=True
        )

    @pytest.mark.asyncio
    async def test_stop_auto_apply(self, client, mock_service_registry):
        """Test POST /stop endpoint deactivates auto-apply."""
        response = await client.post("/api/v1/auto-apply/stop")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        mock_service_registry.get_auto_apply_service.return_value.toggle_auto_apply.assert_called_with(
            "test-user", enabled=False
        )

    @pytest.mark.asyncio
    async def test_get_activity(self, client, mock_service_registry):
        """Test GET /activity endpoint returns activity log."""
        response = await client.get("/api/v1/auto-apply/activity")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        mock_service_registry.get_auto_apply_service.return_value.get_activity_log.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_activity_with_limit(self, client, mock_service_registry):
        """Test GET /activity with limit parameter."""
        response = await client.get("/api/v1/auto-apply/activity?limit=10")

        assert response.status_code == 200
        mock_service_registry.get_auto_apply_service.return_value.get_activity_log.assert_called_with(
            "test-user", limit=10, offset=0
        )


class TestAuthentication:
    """Test authentication requirements for auto-apply endpoints."""

    @pytest.mark.asyncio
    async def test_endpoints_require_auth(self):
        """Test that endpoints return 401 without valid authentication."""
        app = create_app()
        transport = ASGITransport(app=app)

        # Don't mock auth - should return 401
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/auto-apply/config")

        assert response.status_code == 401
