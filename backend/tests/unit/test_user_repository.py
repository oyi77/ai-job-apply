"""
Unit tests for UserRepository.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.repositories.user_repository import UserRepository
from src.models.user import User


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_repo(mock_session):
    return UserRepository(mock_session)


@pytest.mark.asyncio
async def test_get_by_email_found(user_repo, mock_session):
    """Test getting user by email when found."""
    mock_user = User(id="1", email="test@example.com", name="Test User")
    
    # Mock execute result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result
    
    user = await user_repo.get_by_email("test@example.com")
    
    assert user is not None
    assert user.email == "test@example.com"
    # Verify execute was called with a select statement
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_email_not_found(user_repo, mock_session):
    """Test getting user by email when not found."""
    # Mock execute result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    user = await user_repo.get_by_email("nonexistent@example.com")
    
    assert user is None


@pytest.mark.asyncio
async def test_create_user(user_repo, mock_session):
    """Test creating a new user."""
    user_data = {
        "email": "new@example.com",
        "hashed_password": "hashed_secret",
        "name": "New User"
    }
    
    created_user = await user_repo.create(user_data)
    
    assert created_user.email == "new@example.com"
    assert created_user.name == "New User"
    # Verify add and commit were called
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
