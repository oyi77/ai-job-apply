"""
Unit tests for UserSessionRepository.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.user_session_repository import UserSessionRepository
from src.models.user_session import UserSession


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def session_repo(mock_session):
    return UserSessionRepository(mock_session)


@pytest.mark.asyncio
async def test_create_session(session_repo, mock_session):
    """Test creating a new session."""
    user_id = "user123"
    token = "refresh_token_123"
    user_agent = "Mozilla/5.0"
    ip_address = "127.0.0.1"
    
    session = await session_repo.create(
        user_id=user_id,
        refresh_token=token,
        user_agent=user_agent,
        ip_address=ip_address
    )
    
    assert session.user_id == user_id
    assert session.refresh_token == token
    assert session.user_agent == user_agent
    assert session.ip_address == ip_address
    assert session.is_active is True
    
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_token(session_repo, mock_session):
    """Test getting session by refresh token."""
    token = "refresh_token_123"
    mock_session_obj = UserSession(refresh_token=token, user_id="user123")
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_session_obj
    mock_session.execute.return_value = mock_result
    
    session = await session_repo.get_by_token(token)
    
    assert session is not None
    assert session.refresh_token == token


@pytest.mark.asyncio
async def test_invalidate_session(session_repo, mock_session):
    """Test invalidating a session."""
    token = "refresh_token_123"
    mock_session_obj = UserSession(refresh_token=token, is_active=True)
    
    # Mock get_by_token to return the session
    session_repo.get_by_token = AsyncMock(return_value=mock_session_obj)
    
    result = await session_repo.invalidate_session(token)
    
    assert result is True
    assert mock_session_obj.is_active is False
    mock_session.commit.assert_called_once()
