"""Integration tests for password reset functionality."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.app import create_app
from ...database.config import database_config
from ...database.repositories.user_repository import UserRepository
from ...models.user import UserRegister, PasswordResetRequest, PasswordReset
from ...services.auth_service import JWTAuthService


@pytest.fixture
def test_user_data():
    """Test user registration data."""
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "name": "Test User"
    }


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.mark.asyncio
async def test_request_password_reset_success(client, test_user_data):
    """Test successful password reset request."""
    # Register a user first
    register_response = client.post("/api/v1/auth/register", json=test_user_data)
    assert register_response.status_code == 201
    
    # Request password reset
    reset_request = PasswordResetRequest(email=test_user_data["email"])
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
async def test_reset_password_success(client, test_user_data):
    """Test successful password reset."""
    # Register a user
    register_response = client.post("/api/v1/auth/register", json=test_user_data)
    assert register_response.status_code == 201
    
    # Request password reset
    reset_request = PasswordResetRequest(email=test_user_data["email"])
    request_response = client.post("/api/v1/auth/request-password-reset", json=reset_request.model_dump())
    assert request_response.status_code == 200
    
    # Get reset token from auth service (in production, this would come from email)
    async with database_config.get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_email(test_user_data["email"])
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
        "email": test_user_data["email"],
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
async def test_reset_password_expired_token(client, test_user_data):
    """Test password reset with expired token."""
    # Register a user
    register_response = client.post("/api/v1/auth/register", json=test_user_data)
    assert register_response.status_code == 201
    
    # Request password reset
    reset_request = PasswordResetRequest(email=test_user_data["email"])
    request_response = client.post("/api/v1/auth/request-password-reset", json=reset_request.model_dump())
    assert request_response.status_code == 200
    
    # Manually expire the token
    from datetime import datetime, timedelta
    async with database_config.get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_email(test_user_data["email"])
        # Set expiration to past
        await user_repo.update_password_reset_token(user.id, user.password_reset_token, datetime.utcnow() - timedelta(hours=1))
    
    # Try to reset with expired token
    reset = PasswordReset(token=user.password_reset_token, new_password="NewPass123!")
    response = client.post("/api/v1/auth/reset-password", json=reset.model_dump())
    
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_reset_password_weak_password(client, test_user_data):
    """Test password reset with weak password."""
    # Register a user
    register_response = client.post("/api/v1/auth/register", json=test_user_data)
    assert register_response.status_code == 201
    
    # Request password reset
    reset_request = PasswordResetRequest(email=test_user_data["email"])
    request_response = client.post("/api/v1/auth/request-password-reset", json=reset_request.model_dump())
    assert request_response.status_code == 200
    
    # Get reset token
    async with database_config.get_session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_email(test_user_data["email"])
        assert user is not None
        assert user.password_reset_token is not None
    
    # Try to reset with weak password
    reset = PasswordReset(token=user.password_reset_token, new_password="weak")
    response = client.post("/api/v1/auth/reset-password", json=reset.model_dump())
    
    assert response.status_code == 422  # Validation error
