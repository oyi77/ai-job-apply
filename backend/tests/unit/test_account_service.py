"""Tests for AccountService."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from src.services.account_service import AccountServiceImpl
from src.models.user import User, UserProfile


@pytest.fixture
def mock_user():
    """Create a mock user."""
    now = datetime.utcnow()
    return User(
        id="test-user-id",
        email="test@example.com",
        name="Test User",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Y5Y5Y5Y5",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def mock_auth_service():
    """Create a mock auth service."""
    auth_service = MagicMock()
    auth_service.verify_password = MagicMock(return_value=True)
    return auth_service


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def account_service(mock_user_repository, mock_auth_service):
    """Create an account service with mocked dependencies."""
    return AccountServiceImpl(
        user_repository=mock_user_repository,
        auth_service=mock_auth_service,
    )


class TestGetAccount:
    """Test get_account method."""

    @pytest.mark.asyncio
    async def test_get_account_success(
        self, account_service, mock_user, mock_user_repository
    ):
        """Test successful account retrieval."""
        mock_user_repository.get_by_id.return_value = mock_user

        result = await account_service.get_account("test-user-id")

        assert result is not None
        assert result.id == "test-user-id"
        assert result.email == "test@example.com"
        assert result.name == "Test User"
        # Note: UserProfile may not have is_active field
        mock_user_repository.get_by_id.assert_called_once_with("test-user-id")

    @pytest.mark.asyncio
    async def test_get_account_not_found(self, account_service, mock_user_repository):
        """Test account retrieval when user not found."""
        mock_user_repository.get_by_id.return_value = None

        result = await account_service.get_account("nonexistent-id")

        assert result is None
        mock_user_repository.get_by_id.assert_called_once_with("nonexistent-id")


class TestDeleteAccount:
    """Test delete_account method."""

    @pytest.mark.asyncio
    async def test_delete_account_success(
        self, account_service, mock_user, mock_user_repository, mock_auth_service
    ):
        """Test successful account deletion (soft delete)."""
        mock_user_repository.get_by_id.return_value = mock_user
        mock_auth_service.verify_password.return_value = True

        result = await account_service.delete_account(
            "test-user-id", "correct_password"
        )

        assert result is True
        assert mock_user.is_active is False
        mock_user_repository.update.assert_called_once()
        mock_auth_service.verify_password.assert_called_once_with(
            "correct_password", mock_user.password_hash
        )

    @pytest.mark.asyncio
    async def test_delete_account_user_not_found(
        self, account_service, mock_user_repository
    ):
        """Test account deletion when user not found."""
        mock_user_repository.get_by_id.return_value = None

        with pytest.raises(ValueError, match="User not found"):
            await account_service.delete_account("nonexistent-id", "password")

    @pytest.mark.asyncio
    async def test_delete_account_wrong_password(
        self, account_service, mock_user, mock_user_repository, mock_auth_service
    ):
        """Test account deletion with incorrect password."""
        mock_user_repository.get_by_id.return_value = mock_user
        mock_auth_service.verify_password.return_value = False

        with pytest.raises(ValueError, match="Password is incorrect"):
            await account_service.delete_account("test-user-id", "wrong_password")

        mock_user_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_account_soft_delete(
        self, account_service, mock_user, mock_user_repository, mock_auth_service
    ):
        """Test that deletion is soft delete (data preserved)."""
        mock_user_repository.get_by_id.return_value = mock_user
        mock_auth_service.verify_password.return_value = True

        await account_service.delete_account("test-user-id", "password")

        # User record should be updated, not deleted
        mock_user_repository.update.assert_called_once()
        # User should still exist in DB but marked inactive
        assert mock_user.is_active is False
