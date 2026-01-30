"""Unit tests for SessionManager."""

import json
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.session_manager import SessionManager
from src.database.models import DBSessionCookie


@pytest.fixture
def session_manager():
    """Create a SessionManager instance for testing."""
    return SessionManager()


@pytest.fixture
def sample_cookies():
    """Sample cookies dictionary."""
    return {
        "session_id": "abc123",
        "user_token": "xyz789",
        "preferences": {"theme": "dark"},
    }


@pytest.fixture
def sample_db_session(sample_cookies):
    """Create a sample DBSessionCookie."""
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    session = DBSessionCookie(
        id="session_1",
        user_id="user_123",
        platform="linkedin",
        cookies=json.dumps(sample_cookies),
        expires_at=expires_at,
    )
    return session


class TestSessionManagerInit:
    """Test SessionManager initialization."""

    def test_init_creates_empty_cache(self):
        """Test that initialization creates an empty cache."""
        manager = SessionManager()
        assert manager._cache == {}
        assert manager.logger is not None

    def test_init_sets_repository_class(self):
        """Test that repository class is set."""
        manager = SessionManager()
        from src.database.repositories.session_cookie_repository import (
            SessionCookieRepository,
        )

        assert manager._repository_class == SessionCookieRepository


class TestCacheKeyGeneration:
    """Test cache key generation."""

    def test_get_cache_key(self, session_manager):
        """Test cache key generation."""
        key = session_manager._get_cache_key("user_123", "linkedin")
        assert key == ("user_123", "linkedin")

    def test_get_cache_key_different_platforms(self, session_manager):
        """Test cache keys are different for different platforms."""
        key1 = session_manager._get_cache_key("user_123", "linkedin")
        key2 = session_manager._get_cache_key("user_123", "indeed")
        assert key1 != key2


class TestExpiryChecking:
    """Test expiry checking logic."""

    def test_is_expired_with_past_datetime(self, session_manager):
        """Test that past datetime is marked as expired."""
        past = datetime.now(timezone.utc) - timedelta(days=1)
        assert session_manager._is_expired(past) is True

    def test_is_expired_with_future_datetime(self, session_manager):
        """Test that future datetime is not expired."""
        future = datetime.now(timezone.utc) + timedelta(days=1)
        assert session_manager._is_expired(future) is False

    def test_is_expired_with_current_datetime(self, session_manager):
        """Test that current datetime is marked as expired."""
        now = datetime.now(timezone.utc)
        assert session_manager._is_expired(now) is True

    def test_is_expired_handles_naive_datetime(self, session_manager):
        """Test that naive datetime is handled correctly."""
        naive_past = datetime.now() - timedelta(days=1)
        assert session_manager._is_expired(naive_past) is True


class TestLoadSession:
    """Test load_session method."""

    @pytest.mark.asyncio
    async def test_load_session_from_cache(self, session_manager, sample_cookies):
        """Test loading session from cache."""
        # Populate cache
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        cache_key = ("user_123", "linkedin")
        session_manager._cache[cache_key] = {
            "cookies": sample_cookies,
            "expires_at": expires_at,
        }

        # Load session
        result = await session_manager.load_session("user_123", "linkedin")

        assert result == sample_cookies

    @pytest.mark.asyncio
    async def test_load_session_cache_expired(self, session_manager, sample_cookies):
        """Test that expired cache entries are removed."""
        # Populate cache with expired entry
        expired_time = datetime.now(timezone.utc) - timedelta(days=1)
        cache_key = ("user_123", "linkedin")
        session_manager._cache[cache_key] = {
            "cookies": sample_cookies,
            "expires_at": expired_time,
        }

        # Mock repository to return None
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.get_by_user_platform.return_value = None
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.load_session("user_123", "linkedin")

        # Cache should be cleared
        assert cache_key not in session_manager._cache
        assert result is None

    @pytest.mark.asyncio
    async def test_load_session_from_database(
        self, session_manager, sample_cookies, sample_db_session
    ):
        """Test loading session from database."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.get_by_user_platform.return_value = sample_db_session
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.load_session("user_123", "linkedin")

        assert result == sample_cookies
        # Verify cache was updated
        cache_key = ("user_123", "linkedin")
        assert cache_key in session_manager._cache

    @pytest.mark.asyncio
    async def test_load_session_not_found(self, session_manager):
        """Test loading non-existent session."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.get_by_user_platform.return_value = None
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.load_session("user_123", "linkedin")

        assert result is None

    @pytest.mark.asyncio
    async def test_load_session_expired_in_database(self, session_manager):
        """Test loading expired session from database."""
        # Create expired session
        expired_time = datetime.now(timezone.utc) - timedelta(days=1)
        expired_session = DBSessionCookie(
            id="session_1",
            user_id="user_123",
            platform="linkedin",
            cookies=json.dumps({"token": "abc"}),
            expires_at=expired_time,
        )

        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.get_by_user_platform.return_value = expired_session
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.load_session("user_123", "linkedin")

        assert result is None

    @pytest.mark.asyncio
    async def test_load_session_invalid_json(self, session_manager):
        """Test loading session with invalid JSON cookies."""
        # Create session with invalid JSON
        session = DBSessionCookie(
            id="session_1",
            user_id="user_123",
            platform="linkedin",
            cookies="invalid json {",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )

        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.get_by_user_platform.return_value = session
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.load_session("user_123", "linkedin")

        assert result is None


class TestSaveSession:
    """Test save_session method."""

    @pytest.mark.asyncio
    async def test_save_session_new(self, session_manager, sample_cookies):
        """Test saving a new session."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.get_by_user_platform.return_value = None
            mock_repo.create.return_value = MagicMock()
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.save_session(
                "user_123", "linkedin", sample_cookies
            )

        assert result is True
        # Verify cache was updated
        cache_key = ("user_123", "linkedin")
        assert cache_key in session_manager._cache
        assert session_manager._cache[cache_key]["cookies"] == sample_cookies
        # Verify create was called
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_session_update_existing(
        self, session_manager, sample_cookies, sample_db_session
    ):
        """Test updating an existing session."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.get_by_user_platform.return_value = sample_db_session
            mock_repo.update_cookies.return_value = True
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.save_session(
                "user_123", "linkedin", sample_cookies
            )

        assert result is True
        # Verify update was called
        mock_repo.update_cookies.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_session_update_fails(
        self, session_manager, sample_cookies, sample_db_session
    ):
        """Test handling of failed update."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.get_by_user_platform.return_value = sample_db_session
            mock_repo.update_cookies.return_value = False
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.save_session(
                "user_123", "linkedin", sample_cookies
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_save_session_create_fails(self, session_manager, sample_cookies):
        """Test handling of failed create."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.get_by_user_platform.return_value = None
            mock_repo.create.return_value = None
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.save_session(
                "user_123", "linkedin", sample_cookies
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_save_session_exception_handling(
        self, session_manager, sample_cookies
    ):
        """Test exception handling during save."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_get_repo.side_effect = Exception("Database error")

            result = await session_manager.save_session(
                "user_123", "linkedin", sample_cookies
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_save_session_sets_7day_expiry(self, session_manager, sample_cookies):
        """Test that save_session sets 7-day expiry."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.get_by_user_platform.return_value = None
            mock_repo.create.return_value = MagicMock()
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            await session_manager.save_session("user_123", "linkedin", sample_cookies)

        # Check cache expiry
        cache_key = ("user_123", "linkedin")
        cached_expiry = session_manager._cache[cache_key]["expires_at"]
        now = datetime.now(timezone.utc)

        # Should be approximately 7 days from now (within 1 minute tolerance)
        expected_expiry = now + timedelta(days=7)
        time_diff = abs((cached_expiry - expected_expiry).total_seconds())
        assert time_diff < 60  # Within 1 minute


class TestDeleteSession:
    """Test delete_session method."""

    @pytest.mark.asyncio
    async def test_delete_session_success(self, session_manager, sample_cookies):
        """Test successful session deletion."""
        # Add to cache first
        cache_key = ("user_123", "linkedin")
        session_manager._cache[cache_key] = {
            "cookies": sample_cookies,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        }

        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.delete_by_user_platform.return_value = True
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.delete_session("user_123", "linkedin")

        assert result is True
        # Verify cache was cleared
        assert cache_key not in session_manager._cache

    @pytest.mark.asyncio
    async def test_delete_session_not_in_cache(self, session_manager):
        """Test deleting session not in cache."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.delete_by_user_platform.return_value = True
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.delete_session("user_123", "linkedin")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_session_failure(self, session_manager):
        """Test handling of failed deletion."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.delete_by_user_platform.return_value = False
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.delete_session("user_123", "linkedin")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_session_exception_handling(self, session_manager):
        """Test exception handling during delete."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_get_repo.side_effect = Exception("Database error")

            result = await session_manager.delete_session("user_123", "linkedin")

        assert result is False


class TestClearCache:
    """Test clear_cache method."""

    @pytest.mark.asyncio
    async def test_clear_cache(self, session_manager, sample_cookies):
        """Test clearing all cache entries."""
        # Populate cache
        session_manager._cache[("user_123", "linkedin")] = {
            "cookies": sample_cookies,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        }
        session_manager._cache[("user_456", "indeed")] = {
            "cookies": sample_cookies,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        }

        assert len(session_manager._cache) == 2

        await session_manager.clear_cache()

        assert len(session_manager._cache) == 0


class TestCleanupExpiredSessions:
    """Test cleanup_expired_sessions method."""

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions_success(self, session_manager):
        """Test successful cleanup of expired sessions."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.delete_expired_sessions.return_value = 5
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            result = await session_manager.cleanup_expired_sessions()

        assert result == 5

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions_exception(self, session_manager):
        """Test exception handling during cleanup."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_get_repo.side_effect = Exception("Database error")

            result = await session_manager.cleanup_expired_sessions()

        assert result == 0


class TestIntegration:
    """Integration tests for SessionManager."""

    @pytest.mark.asyncio
    async def test_save_and_load_session(self, session_manager, sample_cookies):
        """Test saving and loading a session."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()

            # First call: save (no existing session)
            mock_repo.get_by_user_platform.return_value = None
            mock_repo.create.return_value = MagicMock()
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            save_result = await session_manager.save_session(
                "user_123", "linkedin", sample_cookies
            )
            assert save_result is True

        # Second call: load (from cache)
        load_result = await session_manager.load_session("user_123", "linkedin")
        assert load_result == sample_cookies

    @pytest.mark.asyncio
    async def test_multiple_platforms_same_user(self, session_manager, sample_cookies):
        """Test managing sessions for multiple platforms for same user."""
        with patch.object(session_manager, "_get_session_repo") as mock_get_repo:
            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_repo.get_by_user_platform.return_value = None
            mock_repo.create.return_value = MagicMock()
            mock_get_repo.return_value.__aenter__.return_value = (
                mock_session,
                mock_repo,
            )

            # Save for multiple platforms
            await session_manager.save_session("user_123", "linkedin", sample_cookies)
            await session_manager.save_session("user_123", "indeed", sample_cookies)

        # Verify both are in cache
        assert ("user_123", "linkedin") in session_manager._cache
        assert ("user_123", "indeed") in session_manager._cache

"""
Extended unit tests for Session Manager - 40+ test cases.
Covers all SessionManager methods with comprehensive mocking and error handling.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from src.services.session_manager import SessionManager
from src.database.repositories.session_cookie_repository import SessionCookieRepository
from src.database.models import DBSessionCookie, DBUser


# Test configuration
TEST_USER_ID = "test-user-789"
TEST_TIMEOUT = 30  # seconds for test operations


# Additional fixtures
@pytest.fixture
def db_session_maker():
    """Create async session maker."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    return Mock()


@pytest.fixture
def session_cookies_dict():
    """Create test session cookies."""
    return {
        'linkedin_session': 'cookie_value_abc123',
        'indeed_session': 'cookie_value_xyz456',
        'glassdoor_session': 'cookie_value_def789',
    }


# Extended test cases
class TestSessionManagerExtended:
    """Extended unit tests for SessionManager."""

    @pytest.mark.asyncio
    async def test_init_with_repository(session_repository):
        """Test initialization with repository."""
        manager = SessionManager(
            session_repository=session_repository,
        user_id=TEST_USER_ID,
            cache_expiry_seconds=3600,
        )
        assert manager is not None
        assert manager.user_id == TEST_USER_ID

    @pytest.mark.asyncio
    async def test_load_session_cache_hit_with_expiry(session_manager):
        """Test loading session from cache that hasn't expired."""
        cache_key = (TEST_USER_ID, 'linkedin')
        future_expiry = datetime.now(timezone.utc) + timedelta(days=7)
        
        # Add session to cache (valid, not expired)
        session_manager._cache[cache_key] = {
            'cookies': session_cookies_dict(),
            'expires_at': future_expiry,
            'cached_at': datetime.now(timezone.utc),
        }

        # Load session (should return from cache)
        result = await session_manager.load_session(
            user_id=TEST_USER_ID,
            platform='linkedin',
        )

        # Verify cache was used (repository not called)
        session_manager.session_repo.get_by_user_platform.assert_not_called()

        # Verify session data
        assert result is not None
        assert result['cookies'] == session_cookies_dict()
        assert result['expires_at'] == future_expiry
        assert result['source'] == 'cache'

    @pytest.mark.asyncio
    async def test_load_session_cache_miss_with_repository(session_manager, session_repository):
        """Test loading session from cache miss (loads from database)."""
        cache_key = (TEST_USER_ID, 'linkedin')
        
        # Cache is empty (will load from database)
        session_manager._cache = {}

        # Setup mock for repository to return session cookie
        mock_cookie = DBSessionCookie(
            id=str(uuid.uuid4()),
            user_id=TEST_USER_ID,
            platform='linkedin',
            cookies=json.dumps(session_cookies_dict()),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session_repository.get_by_user_platform.return_value = mock_cookie

        # Load session (should fetch from database)
        result = await session_manager.load_session(
            user_id=TEST_USER_ID,
            platform='linkedin',
        )

        # Verify repository was called (cache miss)
        session_repository.get_by_user_platform.assert_called_once_with(
            user_id=TEST_USER_ID,
            platform='linkedin',
        )

        # Verify session data
        assert result is not None
        assert result['cookies'] == session_cookies_dict()
        assert result['source'] == 'database'
        assert result['expires_at'] == mock_cookie.expires_at

    @pytest.mark.asyncio
    async def test_load_session_repository_error(session_manager, session_repository):
        """Test handling of repository errors when loading session."""
        # Setup mock for repository to raise exception
        session_repository.get_by_user_platform.side_effect = Exception("Database connection failed")

        # Load session (should handle error gracefully)
        result = await session_manager.load_session(
            user_id=TEST_USER_ID,
            platform='linkedin',
        )

        # Verify error was handled
        assert result is None
        assert session_manager.logger.error.call_count >= 1

    @pytest.mark.asyncio
    async def test_save_session_new(session_manager, session_repository):
        """Test saving new session to database."""
        # Setup mock for repository to return created session
        created_cookie = DBSessionCookie(
            id=str(uuid.uuid4()),
            user_id=TEST_USER_ID,
            platform='linkedin',
            cookies=json.dumps(session_cookies_dict()),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session_repository.create.return_value = created_cookie

        # Save session
        result = await session_manager.save_session(
            user_id=TEST_USER_ID,
            platform='linkedin',
            cookies=session_cookies_dict(),
        )

        # Verify repository was called
        session_repository.create.assert_called_once()

        # Verify session was saved
        assert result is True

        # Verify cache was updated
        cache_key = (TEST_USER_ID, 'linkedin')
        assert cache_key in session_manager._cache
        assert session_manager._cache[cache_key]['cookies'] == session_cookies_dict()
        assert session_manager._cache[cache_key]['expires_at'] is not None

    @pytest.mark.asyncio
    async def test_save_session_update_existing(session_manager, session_repository):
        """Test saving session when one already exists."""
        # Setup mock for repository to return existing session
        existing_cookie = DBSessionCookie(
            id=str(uuid.uuid4()),
            user_id=TEST_USER_ID,
            platform='linkedin',
            cookies=json.dumps(session_cookies_dict()),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session_repository.get_by_user_platform.return_value = existing_cookie

        # Setup mock for repository delete
        session_repository.delete_by_user_platform.return_value = None

        # Save session (should update existing)
        result = await session_manager.save_session(
            user_id=TEST_USER_ID,
            platform='linkedin',
            cookies=session_cookies_dict(),
        )

        # Verify repository operations
        session_repository.get_by_user_platform.assert_called_once()
        session_repository.create.assert_called_once()
        session_repository.delete_by_user_platform.assert_called_once()

        # Verify cache was updated
        cache_key = (TEST_USER_ID, 'linkedin')
        assert cache_key in session_manager._cache

    @pytest.mark.asyncio
    async def test_save_session_repository_error(session_manager, session_repository):
        """Test handling of repository errors when saving session."""
        # Setup mock for repository to raise exception
        session_repository.create.side_effect = Exception("Database connection failed")

        # Save session (should handle error gracefully)
        result = await session_manager.save_session(
            user_id=TEST_USER_ID,
            platform='linkedin',
            cookies=session_cookies_dict(),
        )

