"""Integration tests for authentication API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.api.app import create_app


@pytest.fixture
async def app():
    """Create FastAPI app for testing."""
    return create_app()


@pytest.fixture
async def client(app: FastAPI):
    """Create test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def mock_auth_service():
    """Create a mock auth service."""
    mock_service = AsyncMock()
    
    # Mock successful registration
    mock_service.register_user.return_value = MagicMock(
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        token_type="bearer",
        expires_in=1800
    )
    
    # Mock successful login
    mock_service.login_user.return_value = MagicMock(
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        token_type="bearer",
        expires_in=1800
    )
    
    # Mock successful token refresh
    mock_service.refresh_token.return_value = MagicMock(
        access_token="new-access-token",
        refresh_token="new-refresh-token",
        token_type="bearer",
        expires_in=1800
    )
    
    # Mock successful logout
    mock_service.logout_user.return_value = True
    
    # Mock user profile
    mock_service.get_user_profile.return_value = MagicMock(
        id="test-user-id",
        email="test@example.com",
        name="Test User",
        is_active=True,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00"
    )
    
    # Mock profile update
    mock_service.update_user_profile.return_value = MagicMock(
        id="test-user-id",
        email="test@example.com",
        name="Updated Name",
        is_active=True,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00"
    )
    
    # Mock password change
    mock_service.change_password.return_value = True
    
    # Mock token verification
    mock_service.verify_token.return_value = "test-user-id"
    
    return mock_service


class TestUserRegistration:
    """Test user registration endpoint."""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, mock_auth_service):
        """Test successful user registration."""
        with patch('src.services.service_registry.service_registry.get_auth_service', return_value=mock_auth_service):
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "newuser@example.com",
                    "password": "password123",
                    "name": "New User"
                }
            )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, mock_auth_service):
        """Test registration with duplicate email."""
        mock_auth_service.register_user.side_effect = ValueError("Email already registered")
        
        with patch('src.services.service_registry.service_registry.get_auth_service', return_value=mock_auth_service):
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "existing@example.com",
                    "password": "password123",
                    "name": "New User"
                }
            )
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_register_invalid_data(self, client: AsyncClient):
        """Test registration with invalid data."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",  # Invalid email format
                "password": "short",  # Too short password
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Test user login endpoint."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, mock_auth_service):
        """Test successful user login."""
        with patch('src.services.service_registry.service_registry.get_auth_service', return_value=mock_auth_service):
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "password123"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient, mock_auth_service):
        """Test login with invalid credentials."""
        mock_auth_service.login_user.side_effect = ValueError("Invalid email or password")
        
        with patch('src.services.service_registry.service_registry.get_auth_service', return_value=mock_auth_service):
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrongpassword"
                }
            )
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_missing_fields(self, client: AsyncClient):
        """Test login with missing fields."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com"
                # Missing password
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, mock_auth_service):
        """Test successful token refresh."""
        with patch('src.services.service_registry.service_registry.get_auth_service', return_value=mock_auth_service):
            response = await client.post(
                "/api/v1/auth/refresh",
                json={
                    "refresh_token": "test-refresh-token"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["access_token"] == "new-access-token"
        assert data["refresh_token"] == "new-refresh-token"
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient, mock_auth_service):
        """Test refresh with invalid token."""
        mock_auth_service.refresh_token.side_effect = ValueError("Invalid or expired refresh token")
        
        with patch('src.services.service_registry.service_registry.get_auth_service', return_value=mock_auth_service):
            response = await client.post(
                "/api/v1/auth/refresh",
                json={
                    "refresh_token": "invalid-token"
                }
            )
        
        assert response.status_code == 401
        assert "Invalid or expired refresh token" in response.json()["detail"]


class TestUserLogout:
    """Test user logout endpoint."""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient, mock_auth_service):
        """Test successful logout."""
        # Mock get_current_user dependency
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        
        with patch('src.api.v1.auth.get_current_user', return_value=mock_user):
            with patch('src.services.service_registry.service_registry.get_auth_service', return_value=mock_auth_service):
                response = await client.post(
                    "/api/v1/auth/logout",
                    json={
                        "refresh_token": "test-refresh-token"
                    },
                    headers={"Authorization": "Bearer test-access-token"}
                )
        
        assert response.status_code == 200
        assert "message" in response.json()
    
    @pytest.mark.asyncio
    async def test_logout_unauthorized(self, client: AsyncClient):
        """Test logout without authentication."""
        response = await client.post(
            "/api/v1/auth/logout",
            json={
                "refresh_token": "test-refresh-token"
            }
        )
        
        assert response.status_code == 403  # Forbidden (no auth token)


class TestUserProfile:
    """Test user profile endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_profile_success(self, client: AsyncClient, mock_auth_service):
        """Test getting user profile."""
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_user.is_active = True
        
        with patch('src.api.v1.auth.get_current_user', return_value=mock_user):
            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": "Bearer test-access-token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-user-id"
        assert data["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_profile_unauthorized(self, client: AsyncClient):
        """Test getting profile without authentication."""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # Forbidden
    
    @pytest.mark.asyncio
    async def test_update_profile_success(self, client: AsyncClient, mock_auth_service):
        """Test updating user profile."""
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        
        with patch('src.api.v1.auth.get_current_user', return_value=mock_user):
            with patch('src.services.service_registry.service_registry.get_auth_service', return_value=mock_auth_service):
                response = await client.put(
                    "/api/v1/auth/me",
                    json={
                        "name": "Updated Name"
                    },
                    headers={"Authorization": "Bearer test-access-token"}
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
    
    @pytest.mark.asyncio
    async def test_update_profile_email_taken(self, client: AsyncClient, mock_auth_service):
        """Test updating profile with email already in use."""
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        
        mock_auth_service.update_user_profile.side_effect = ValueError("Email already in use")
        
        with patch('src.api.v1.auth.get_current_user', return_value=mock_user):
            with patch('src.services.service_registry.service_registry.get_auth_service', return_value=mock_auth_service):
                response = await client.put(
                    "/api/v1/auth/me",
                    json={
                        "email": "taken@example.com"
                    },
                    headers={"Authorization": "Bearer test-access-token"}
                )
        
        assert response.status_code == 400
        assert "Email already in use" in response.json()["detail"]


class TestPasswordChange:
    """Test password change endpoint."""
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, client: AsyncClient, mock_auth_service):
        """Test successful password change."""
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        
        with patch('src.api.v1.auth.get_current_user', return_value=mock_user):
            with patch('src.services.service_registry.service_registry.get_auth_service', return_value=mock_auth_service):
                response = await client.post(
                    "/api/v1/auth/change-password",
                    json={
                        "current_password": "oldpassword123",
                        "new_password": "newpassword456"
                    },
                    headers={"Authorization": "Bearer test-access-token"}
                )
        
        assert response.status_code == 200
        assert "message" in response.json()
    
    @pytest.mark.asyncio
    async def test_change_password_incorrect_current(self, client: AsyncClient, mock_auth_service):
        """Test password change with incorrect current password."""
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        
        mock_auth_service.change_password.side_effect = ValueError("Current password is incorrect")
        
        with patch('src.api.v1.auth.get_current_user', return_value=mock_user):
            with patch('src.services.service_registry.service_registry.get_auth_service', return_value=mock_auth_service):
                response = await client.post(
                    "/api/v1/auth/change-password",
                    json={
                        "current_password": "wrongpassword",
                        "new_password": "newpassword456"
                    },
                    headers={"Authorization": "Bearer test-access-token"}
                )
        
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_change_password_unauthorized(self, client: AsyncClient):
        """Test password change without authentication."""
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword456"
            }
        )
        
        assert response.status_code == 403  # Forbidden


class TestProtectedRoutes:
    """Test that protected routes require authentication."""
    
    @pytest.mark.asyncio
    async def test_protected_route_without_auth(self, client: AsyncClient):
        """Test accessing protected route without authentication."""
        response = await client.get("/api/v1/applications")
        
        assert response.status_code == 403  # Forbidden
    
    @pytest.mark.asyncio
    async def test_protected_route_with_invalid_token(self, client: AsyncClient):
        """Test accessing protected route with invalid token."""
        response = await client.get(
            "/api/v1/applications",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401  # Unauthorized
    
    @pytest.mark.asyncio
    async def test_protected_route_with_valid_token(self, client: AsyncClient, mock_auth_service):
        """Test accessing protected route with valid token."""
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_user.is_active = True
        
        # Mock the application service
        mock_app_service = AsyncMock()
        mock_app_service.get_all_applications.return_value = ([], 0)
        
        with patch('src.api.dependencies.get_current_user', return_value=mock_user):
            with patch('src.services.service_registry.service_registry.get_application_service', return_value=mock_app_service):
                response = await client.get(
                    "/api/v1/applications",
                    headers={"Authorization": "Bearer valid-token"}
                )
        
        # Should succeed (status depends on implementation)
        assert response.status_code in [200, 404]  # 200 if empty list, 404 if not found

