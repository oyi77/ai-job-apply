"""
Integration tests for Protected API endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from src.api.app import create_app
from src.database.config import database_config, Base
from src.core.cache import cache_region


@pytest.fixture
async def setup_database():
    """Setup test database."""
    cache_region.configure("dogpile.cache.memory", replace_existing_backend=True)
    cache_region.invalidate()
    
    async with database_config.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with database_config.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await database_config.close()


@pytest.fixture
async def client(setup_database):
    """Create test client."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_protected_route_unauthorized(client):
    """Test accessing protected route without token."""
    response = await client.get("/api/v1/applications")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_authorized(client):
    """Test accessing protected route with valid token."""
    # Register and login
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User"
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123!"
    }
    login_res = await client.post("/api/v1/auth/login", data=login_data)
    access_token = login_res.json()["access_token"]
    
    # Access protected route
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/v1/applications", headers=headers)
    
    # Should be 200 OK (empty list)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_user_data_isolation(client):
    """Test that users can only see their own data."""
    # User 1
    user1_data = {
        "email": "user1@example.com",
        "password": "Password123!",
        "name": "User One"
    }
    await client.post("/api/v1/auth/register", json=user1_data)
    
    login1_res = await client.post("/api/v1/auth/login", data={"username": "user1@example.com", "password": "Password123!"})
    token1 = login1_res.json()["access_token"]
    
    # User 2
    user2_data = {
        "email": "user2@example.com",
        "password": "Password123!",
        "name": "User Two"
    }
    await client.post("/api/v1/auth/register", json=user2_data)
    
    login2_res = await client.post("/api/v1/auth/login", data={"username": "user2@example.com", "password": "Password123!"})
    token2 = login2_res.json()["access_token"]
    
    # User 1 creates application
    app_data = {
        "job_title": "Software Engineer",
        "company": "Tech Corp",
        "status": "applied"
    }
    headers1 = {"Authorization": f"Bearer {token1}"}
    await client.post("/api/v1/applications", json=app_data, headers=headers1)
    
    # User 2 checks applications
    headers2 = {"Authorization": f"Bearer {token2}"}
    response = await client.get("/api/v1/applications", headers=headers2)
    
    # User 2 should see empty list (data isolation)
    assert response.status_code == 200
    assert len(response.json()) == 0
    
    # User 1 checks applications
    response = await client.get("/api/v1/applications", headers=headers1)
    assert len(response.json()) == 1
