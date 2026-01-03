"""Unit tests for authentication service."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from jose import jwt

from src.services.auth_service import JWTAuthService
from src.models.user import UserRegister, UserLogin, UserProfileUpdate, PasswordChange
from src.config import config


@pytest.fixture
async def auth_service():
    """Create an auth service instance for testing."""
    service = JWTAuthService()
    # Mock the repository and session
    mock_repo = AsyncMock()
    mock_session = AsyncMock()
    
    # Mock the _get_session_repo context manager
    service._get_session_repo = MagicMock()
    service._get_session_repo.return_value.__aenter__.return_value = (mock_session, mock_repo)
    
    # Keep references for assertions
    service._repository = mock_repo
    service._session = mock_session
    
    return service


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    from src.models.user import User
    # Note: This is a mock hash - in real tests, we'd use actual bcrypt hashing
    return User(
        id="test-user-id",
        email="test@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5",  # bcrypt hash for "Password123"
        name="Test User",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    @pytest.mark.asyncio
    async def test_hash_password(self, auth_service):
        """Test password hashing."""
        password = "TestPassword123"
        hashed = auth_service._hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash format
    
    @pytest.mark.asyncio
    async def test_verify_password_correct(self, auth_service):
        """Test password verification with correct password."""
        password = "TestPassword123"
        hashed = auth_service._hash_password(password)
        
        assert auth_service._verify_password(password, hashed) is True
    
    @pytest.mark.asyncio
    async def test_verify_password_incorrect(self, auth_service):
        """Test password verification with incorrect password."""
        password = "TestPassword123"
        wrong_password = "WrongPassword"
        hashed = auth_service._hash_password(password)
        
        assert auth_service._verify_password(wrong_password, hashed) is False


class TestTokenCreation:
    """Test JWT token creation."""
    
    @pytest.mark.asyncio
    async def test_create_access_token(self, auth_service):
        """Test access token creation."""
        user_id = "test-user-id"
        email = "test@example.com"
        token = auth_service._create_access_token(user_id, email)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify token
        payload = jwt.decode(
            token,
            config.jwt_secret_key,
            algorithms=[config.jwt_algorithm]
        )
        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["type"] == "access"
        assert "exp" in payload
    
    @pytest.mark.asyncio
    async def test_create_refresh_token(self, auth_service):
        """Test refresh token creation."""
        user_id = "test-user-id"
        token = auth_service._create_refresh_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify token
        payload = jwt.decode(
            token,
            config.jwt_secret_key,
            algorithms=[config.jwt_algorithm]
        )
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload


class TestUserRegistration:
    """Test user registration."""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, sample_user):
        """Test successful user registration."""
        registration = UserRegister(
            email="newuser@example.com",
            password="Password123",
            name="New User"
        )
        
        # Mock repository methods
        auth_service._repository.get_by_email.return_value = None  # User doesn't exist
        auth_service._repository.create.return_value = sample_user
        auth_service._repository.create_session.return_value = MagicMock()
        
        response = await auth_service.register_user(registration)
        
        assert response.access_token is not None
        assert response.refresh_token is not None
        assert response.token_type == "bearer"
        assert response.expires_in > 0
        
        # Verify repository was called
        auth_service._repository.get_by_email.assert_called_once()
        auth_service._repository.create.assert_called_once()
        auth_service._repository.create_session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, auth_service, sample_user):
        """Test registration with duplicate email."""
        registration = UserRegister(
            email="existing@example.com",
            password="Password123",
            name="New User"
        )
        
        # Mock repository to return existing user
        auth_service._repository.get_by_email.return_value = sample_user
        
        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.register_user(registration)


class TestUserLogin:
    """Test user login."""
    
    @pytest.mark.asyncio
    async def test_login_user_success(self, auth_service, sample_user):
        """Test successful user login."""
        login_data = UserLogin(
            email="test@example.com",
            password="Password123"
        )
        
        # Mock repository methods
        auth_service._repository.get_by_email.return_value = sample_user
        auth_service._repository.create_session.return_value = MagicMock()
        
        # Mock password verification (we'll use actual bcrypt in real tests)
        with patch.object(auth_service, '_verify_password', return_value=True):
            response = await auth_service.login_user(login_data)
        
        assert response.access_token is not None
        assert response.refresh_token is not None
        assert response.token_type == "bearer"
        assert response.expires_in > 0
        
        # Verify repository was called
        auth_service._repository.get_by_email.assert_called_once()
        auth_service._repository.create_session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_login_user_invalid_email(self, auth_service):
        """Test login with non-existent email."""
        login_data = UserLogin(
            email="nonexistent@example.com",
            password="Password123"
        )
        
        # Mock repository to return None (user doesn't exist)
        auth_service._repository.get_by_email.return_value = None
        
        with pytest.raises(ValueError, match="Invalid email or password"):
            await auth_service.login_user(login_data)
    
    @pytest.mark.asyncio
    async def test_login_user_invalid_password(self, auth_service, sample_user):
        """Test login with incorrect password."""
        login_data = UserLogin(
            email="test@example.com",
            password="wrongpassword"
        )
        
        # Mock repository methods
        auth_service._repository.get_by_email.return_value = sample_user
        # Mock account lockout methods (may be called if lockout is enabled)
        auth_service._repository.increment_failed_login_attempts.return_value = 1
        auth_service._repository.lock_account.return_value = True
        
        # Mock password verification to return False
        with patch.object(auth_service, '_verify_password', return_value=False):
            with patch('src.config.config.account_lockout_enabled', False):
                with pytest.raises(ValueError, match="Invalid email or password"):
                    await auth_service.login_user(login_data)
    
    @pytest.mark.asyncio
    async def test_login_user_inactive(self, auth_service, sample_user):
        """Test login with inactive user."""
        login_data = UserLogin(
            email="test@example.com",
            password="Password123"
        )
        
        # Create inactive user
        inactive_user = sample_user.model_copy()
        inactive_user.is_active = False
        
        # Mock repository methods
        auth_service._repository.get_by_email.return_value = inactive_user
        
        with pytest.raises(ValueError, match="Account is disabled"):
            await auth_service.login_user(login_data)


class TestTokenRefresh:
    """Test token refresh."""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, auth_service, sample_user):
        """Test successful token refresh."""
        # Create a valid refresh token
        refresh_token = auth_service._create_refresh_token(sample_user.id)
        
        # Mock repository methods
        mock_session = MagicMock()
        mock_session.user_id = sample_user.id
        mock_session.is_active = True
        
        auth_service._repository.get_session.return_value = mock_session
        auth_service._repository.get_by_id.return_value = sample_user
        auth_service._repository.invalidate_session.return_value = True
        auth_service._repository.create_session.return_value = MagicMock()
        
        response = await auth_service.refresh_token(refresh_token)
        
        assert response.access_token is not None
        assert response.refresh_token is not None
        assert response.token_type == "bearer"
        assert response.expires_in > 0
        
        # Verify old session was invalidated and new one created
        auth_service._repository.invalidate_session.assert_called_once()
        auth_service._repository.create_session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, auth_service):
        """Test refresh with invalid token."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(ValueError, match="Invalid or expired refresh token"):
            await auth_service.refresh_token(invalid_token)
    
    @pytest.mark.asyncio
    async def test_refresh_token_expired_session(self, auth_service, sample_user):
        """Test refresh with expired session."""
        refresh_token = auth_service._create_refresh_token(sample_user.id)
        
        # Mock repository to return None (session doesn't exist or expired)
        auth_service._repository.get_session.return_value = None
        
        with pytest.raises(ValueError, match="Invalid or expired refresh token"):
            await auth_service.refresh_token(refresh_token)


class TestUserProfile:
    """Test user profile operations."""
    
    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, auth_service, sample_user):
        """Test getting user profile."""
        auth_service._repository.get_by_id.return_value = sample_user
        
        profile = await auth_service.get_user_profile(sample_user.id)
        
        assert profile is not None
        assert profile.id == sample_user.id
        assert profile.email == sample_user.email
        assert profile.name == sample_user.name
    
    @pytest.mark.asyncio
    async def test_get_user_profile_not_found(self, auth_service):
        """Test getting profile for non-existent user."""
        auth_service._repository.get_by_id.return_value = None
        
        profile = await auth_service.get_user_profile("nonexistent-id")
        
        assert profile is None
    
    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, auth_service, sample_user):
        """Test updating user profile."""
        updates = UserProfileUpdate(name="Updated Name")
        
        updated_user = sample_user.model_copy()
        updated_user.name = "Updated Name"
        
        auth_service._repository.get_by_email.return_value = None  # Email not taken
        auth_service._repository.update.return_value = updated_user
        
        profile = await auth_service.update_user_profile(sample_user.id, updates)
        
        assert profile.name == "Updated Name"
        auth_service._repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_user_profile_email_taken(self, auth_service, sample_user):
        """Test updating profile with email already in use."""
        updates = UserProfileUpdate(email="taken@example.com")
        
        existing_user = sample_user.model_copy()
        existing_user.id = "different-id"
        
        auth_service._repository.get_by_email.return_value = existing_user
        
        with pytest.raises(ValueError, match="Email already in use"):
            await auth_service.update_user_profile(sample_user.id, updates)


class TestPasswordChange:
    """Test password change."""
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, auth_service, sample_user):
        """Test successful password change."""
        password_change = PasswordChange(
            current_password="Password123",
            new_password="NewPassword456"
        )
        
        auth_service._repository.get_by_id.return_value = sample_user
        auth_service._repository.update_password.return_value = True
        auth_service._repository.invalidate_all_user_sessions.return_value = True
        
        # Mock password verification
        with patch.object(auth_service, '_verify_password', return_value=True):
            success = await auth_service.change_password(sample_user.id, password_change)
        
        assert success is True
        auth_service._repository.update_password.assert_called_once()
        auth_service._repository.invalidate_all_user_sessions.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_change_password_incorrect_current(self, auth_service, sample_user):
        """Test password change with incorrect current password."""
        password_change = PasswordChange(
            current_password="WrongPassword",
            new_password="NewPassword456"
        )
        
        auth_service._repository.get_by_id.return_value = sample_user
        
        # Mock password verification to return False
        with patch.object(auth_service, '_verify_password', return_value=False):
            with pytest.raises(ValueError, match="Current password is incorrect"):
                await auth_service.change_password(sample_user.id, password_change)


class TestTokenVerification:
    """Test token verification."""
    
    @pytest.mark.asyncio
    async def test_verify_token_success(self, auth_service, sample_user):
        """Test successful token verification."""
        token = auth_service._create_access_token(sample_user.id, sample_user.email)
        
        user_id = await auth_service.verify_token(token)
        
        assert user_id == sample_user.id
    
    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, auth_service):
        """Test verification with invalid token."""
        invalid_token = "invalid.token.here"
        
        user_id = await auth_service.verify_token(invalid_token)
        
        assert user_id is None
    
    @pytest.mark.asyncio
    async def test_verify_token_wrong_type(self, auth_service, sample_user):
        """Test verification with refresh token (wrong type)."""
        refresh_token = auth_service._create_refresh_token(sample_user.id)
        
        user_id = await auth_service.verify_token(refresh_token)
        
        assert user_id is None  # Should return None for refresh tokens


class TestLogout:
    """Test user logout."""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, auth_service, sample_user):
        """Test successful logout."""
        refresh_token = "test-refresh-token"
        
        mock_session = MagicMock()
        mock_session.user_id = sample_user.id
        
        auth_service._repository.get_session.return_value = mock_session
        auth_service._repository.invalidate_session.return_value = True
        
        success = await auth_service.logout_user(refresh_token, sample_user.id)
        
        assert success is True
        auth_service._repository.invalidate_session.assert_called_once_with(refresh_token)
    
    @pytest.mark.asyncio
    async def test_logout_invalid_session(self, auth_service, sample_user):
        """Test logout with invalid session - always returns True for frontend cleanup."""
        refresh_token = "invalid-refresh-token"
        
        auth_service._repository.get_session.return_value = None
        
        success = await auth_service.logout_user(refresh_token, sample_user.id)
        
        # Logout always returns True to allow frontend cleanup, even if session is invalid
        assert success is True
    
    @pytest.mark.asyncio
    async def test_logout_wrong_user(self, auth_service, sample_user):
        """Test logout with session belonging to different user - always returns True for frontend cleanup."""
        refresh_token = "test-refresh-token"
        
        mock_session = MagicMock()
        mock_session.user_id = "different-user-id"
        
        auth_service._repository.get_session.return_value = mock_session
        
        success = await auth_service.logout_user(refresh_token, sample_user.id)
        
        # Logout always returns True to allow frontend cleanup, even if session belongs to different user
        assert success is True

