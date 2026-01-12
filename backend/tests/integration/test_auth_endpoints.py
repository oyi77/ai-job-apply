"""
Integration tests for Authentication API endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta

from src.api.app import create_app
from src.database.config import database_config, Base
from src.core.cache import cache_region
from src.core.security import get_password_hash


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


@pytest.mark.asyncio
async def test_register_user_success(client):
    """Test user registration endpoint."""
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_user_duplicate_email(client):
    """Test registration with existing email."""
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User"
    }
    
    # Register first user
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Try to register again
    response = await client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client):
    """Test login endpoint."""
    # Register user
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User"
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Login
    login_data = {
        "username": "test@example.com",  # OAuth2 password flow uses username field
        "password": "TestPassword123!"
    }
    
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Test login with wrong password."""
    # Register user
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User"
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Login with wrong password
    login_data = {
        "username": "test@example.com",
        "password": "WrongPassword!"
    }
    
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_token_success(client):
    """Test token refresh endpoint."""
    # Register user
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User"
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Login to get refresh token
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123!"
    }
    login_res = await client.post("/api/v1/auth/login", data=login_data)
    refresh_token = login_res.json()["refresh_token"]
    
    # Refresh token
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh_token  # Should rotate token


@pytest.mark.asyncio
async def test_get_profile(client):
    """Test get user profile endpoint."""
    # Register user
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User"
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Login to get access token
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123!"
    }
    login_res = await client.post("/api/v1/auth/login", data=login_data)
    access_token = login_res.json()["access_token"]
    
    # Get profile
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"


@pytest.mark.asyncio
async def test_delete_account_success(client):
    """Test account deletion endpoint."""
    # Register user
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User"
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Login to get access token
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123!"
    }
    login_res = await client.post("/api/v1/auth/login", data=login_data)
    access_token = login_res.json()["access_token"]
    
    # Delete account
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.delete(
        "/api/v1/auth/account",
        headers=headers,
        json={"password": "TestPassword123!"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "deleted" in data["message"].lower()
    
    # Verify user cannot login after deletion
    login_res = await client.post("/api/v1/auth/login", data=login_data)
    assert login_res.status_code == 401


@pytest.mark.asyncio
async def test_delete_account_wrong_password(client):
    """Test account deletion with wrong password."""
    # Register user
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "name": "Test User"
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Login to get access token
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123!"
    }
    login_res = await client.post("/api/v1/auth/login", data=login_data)
    access_token = login_res.json()["access_token"]
    
    # Try to delete account with wrong password
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.delete(
        "/api/v1/auth/account",
        headers=headers,
        json={"password": "WrongPassword!"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "password" in data["detail"].lower() or "incorrect" in data["detail"].lower()


@pytest.mark.asyncio
async def test_delete_account_unauthorized(client):
    """Test account deletion without authentication."""
    response = await client.delete(
        "/api/v1/auth/account",
        json={"password": "TestPassword123!"}
    )
    
    assert response.status_code == 401
