"""
Integration tests for Analytics API endpoints
"""

import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone

from src.api.app import create_app
from src.database.config import database_config, Base
from src.core.cache import cache_region


@pytest.fixture
async def setup_database():
    """Setup test database."""
    # Configure cache for testing
    cache_region.configure("dogpile.cache.memory", replace_existing_backend=True)
    cache_region.invalidate()
    
    # Setup database
    async with database_config.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Teardown
    async with database_config.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await database_config.close()


@pytest.fixture
async def client(setup_database):
    """Create test client."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def get_auth_headers(client: AsyncClient) -> dict:
    """Get authentication headers for test user."""
    # Register user
    register_data = {
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User"
    }
    await client.post("/api/v1/auth/register", json=register_data)
    
    # Login
    login_data = {
        "username": "test@example.com",
        "password": "TestPass123!"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    token_data = response.json()
    
    # Extract token
    if isinstance(token_data, dict) and "access_token" in token_data:
        token = token_data["access_token"]
    elif isinstance(token_data, dict) and "data" in token_data:
        token = token_data["data"].get("access_token")
    else:
        token = token_data.get("token", "")
    
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_success_rate_metrics(client):
    """Test success rate metrics endpoint."""
    headers = await get_auth_headers(client)
    
    response = await client.get("/api/v1/analytics/metrics/success-rate", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total_applications" in data["data"]
    assert "success_rate" in data["data"]
    assert "breakdown" in data["data"]


@pytest.mark.asyncio
async def test_get_response_time_metrics(client):
    """Test response time metrics endpoint."""
    headers = await get_auth_headers(client)
    
    response = await client.get("/api/v1/analytics/metrics/response-time", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "avg_response_time_days" in data["data"]


@pytest.mark.asyncio
async def test_get_interview_performance(client):
    """Test interview performance endpoint."""
    headers = await get_auth_headers(client)
    
    response = await client.get("/api/v1/analytics/metrics/interview-performance", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total_interviews" in data["data"]
    assert "interview_to_offer_rate" in data["data"]


@pytest.mark.asyncio
async def test_get_trend_analysis(client):
    """Test trend analysis endpoint."""
    headers = await get_auth_headers(client)
    
    response = await client.get("/api/v1/analytics/trends?days=30", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "weekly_trends" in data["data"]


@pytest.mark.asyncio
async def test_get_skills_gap_analysis(client):
    """Test skills gap analysis endpoint."""
    headers = await get_auth_headers(client)
    
    response = await client.get("/api/v1/analytics/insights/skills-gap", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "top_required_skills" in data["data"]


@pytest.mark.asyncio
async def test_get_company_analysis(client):
    """Test company analysis endpoint."""
    headers = await get_auth_headers(client)
    
    response = await client.get("/api/v1/analytics/insights/companies", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "companies" in data["data"]


@pytest.mark.asyncio
async def test_get_analytics_dashboard(client):
    """Test comprehensive dashboard endpoint."""
    headers = await get_auth_headers(client)
    
    response = await client.get("/api/v1/analytics/dashboard", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    
    # Verify all sections are present
    dashboard_data = data["data"]
    assert "success_metrics" in dashboard_data
    assert "response_time_metrics" in dashboard_data
    assert "interview_metrics" in dashboard_data
    assert "trends" in dashboard_data
    assert "skills_gap" in dashboard_data
    assert "companies" in dashboard_data


@pytest.mark.asyncio
async def test_export_analytics_csv(client):
    """Test CSV export functionality."""
    headers = await get_auth_headers(client)
    
    response = await client.get("/api/v1/analytics/export?format=csv", headers=headers)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "Content-Disposition" in response.headers


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    """Test that endpoints require authentication."""
    response = await client.get("/api/v1/analytics/metrics/success-rate")
    
    assert response.status_code == 401  # Unauthorized
