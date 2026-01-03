"""Integration tests for password reset functionality."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.app import create_app
from src.database.config import database_config
from src.database.repositories.user_repository import UserRepository
from src.models.user import UserRegister, PasswordResetRequest, PasswordReset
from src.services.auth_service import JWTAuthService


@pytest.fixture
def test_user_data():
    """Test user registration data."""
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "name": "Test User"
    }


@pytest.fixture(autouse=True)
async def db_setup():
    """Initialize test database and clear tables before each test."""
    from src.services.service_registry import service_registry
    import os
    
    # Shut down registry first to close active sessions
    await service_registry.shutdown()
    
    # Close database and remove file to ensure clean state
    await database_config.close()
    db_file = "test_ai_job_assistant.db"
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass
            
    await database_config.initialize(test_mode=True)
    await database_config.create_tables()
    
    yield
    
    await service_registry.shutdown()
    await database_config.close()


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.mark.asyncio
async def test_request_password_reset_success(client):
    """Test successful password reset request."""
    email = "reset_success@example.com"
    test_user_data = {
        "email": email,
        "password": "TestPass123!",
        "name": "Test User"
    }
    # Register a user first
    register_response = client.post("/api/v1/auth/register", json=test_user_data)
    assert register_response.status_code == 201
    
    # Request password reset
    reset_request = PasswordResetRequest(email=email)
    response = client.post("/api/v1/auth/request-password-reset", json=reset_request.model_dump())
    
    assert response.status_code == 200
    assert "message" in response.json()
    assert "password reset link" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_request_password_reset_nonexistent_email(client):
    """Test password reset request for non-existent email (security: should still return success)."""
    reset_request = PasswordResetRequest(email="nonexistent@example.com")
    response = client.post("/api/v1/auth/request-password-reset", json=reset_request.model_dump())
    
    # Should return success to prevent email enumeration
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_reset_password_success(client):
    """Test successful password reset."""
    email = "reset_flow_success@example.com"
    test_user_data = {
        "email": email,
        "password": "TestPass123!",
        "name": "Test User"
    }
    # Register a user
    register_response = client.post("/api/v1/auth/register", json=test_user_data)
    assert register_response.status_code == 201
    
    # Request password reset
    reset_request = PasswordResetRequest(email=email)
    request_response = client.post("/api/v1/auth/request-password-reset", json=reset_request.model_dump())
    assert request_response.status_code == 200
    
    # Get reset token from auth service (in production, this would come from email)
    async with database_config.get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_email(email)
        assert user is not None
        assert user.password_reset_token is not None
    
    # Reset password with token
    new_password = "NewPass123!"
    reset = PasswordReset(token=user.password_reset_token, new_password=new_password)
    response = client.post("/api/v1/auth/reset-password", json=reset.model_dump())
    
    assert response.status_code == 200
    assert "successfully" in response.json()["message"].lower()
    
    # Verify new password works
    login_response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": new_password
    })
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client):
    """Test password reset with invalid token."""
    reset = PasswordReset(token="invalid_token", new_password="NewPass123!")
    response = client.post("/api/v1/auth/reset-password", json=reset.model_dump())
    
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower() or "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_reset_password_expired_token(client):
    """Test password reset with expired token."""
    email = "reset_expired@example.com"
    test_user_data = {
        "email": email,
        "password": "TestPass123!",
        "name": "Test User"
    }
    # Register a user
    register_response = client.post("/api/v1/auth/register", json=test_user_data)
    assert register_response.status_code == 201
    
    # Request password reset
    reset_request = PasswordResetRequest(email=email)
    request_response = client.post("/api/v1/auth/request-password-reset", json=reset_request.model_dump())
    assert request_response.status_code == 200
    
    # Manually expire the token
    from datetime import datetime, timezone, timedelta
    async with database_config.get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_email(email)
        # Set expiration to past
        await user_repo.update_password_reset_token(user.id, user.password_reset_token, datetime.now(timezone.utc) - timedelta(hours=1))
    
    # Try to reset with expired token
    reset = PasswordReset(token=user.password_reset_token, new_password="NewPass123!")
    response = client.post("/api/v1/auth/reset-password", json=reset.model_dump())
    
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_reset_password_weak_password(client):
    """Test password reset with weak password."""
    email = "reset_weak@example.com"
    test_user_data = {
        "email": email,
        "password": "TestPass123!",
        "name": "Test User"
    }
    # Register a user
    register_response = client.post("/api/v1/auth/register", json=test_user_data)
    assert register_response.status_code == 201
    
    # Request password reset
    reset_request = PasswordResetRequest(email=email)
    request_response = client.post("/api/v1/auth/request-password-reset", json=reset_request.model_dump())
    assert request_response.status_code == 200
    
    # Get reset token
    async with database_config.get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_email(email)
        assert user is not None
        assert user.password_reset_token is not None
    
    # Try to reset with weak password
    response = client.post("/api/v1/auth/reset-password", json={
        "token": user.password_reset_token,
        "new_password": "weak"
    })
    
    assert response.status_code == 422  # Validation error
