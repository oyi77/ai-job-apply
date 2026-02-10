"""Unit tests for FailureLoggerService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
import uuid

from src.services.failure_logger import FailureLoggerService
from src.database.models import DBFailureLog
from src.models.failure_log import FailureLog

TEST_USER_ID = "test-user-123"


@pytest.fixture
def mock_session():
    session = AsyncMock()
    # Mock execute result
    session.execute.return_value = MagicMock()
    # Mock begin context manager
    session.begin = MagicMock()
    session.begin.return_value.__aenter__.return_value = session
    return session


@pytest.fixture
def failure_logger(mock_session):
    return FailureLoggerService(mock_session, TEST_USER_ID)


@pytest.mark.asyncio
class TestFailureLogger:
    async def test_log_error_creates_log(self, failure_logger, mock_session):
        """Test log_error creates a DBFailureLog."""
        # Setup session context manager for begin()
        mock_session.begin.return_value.__aenter__.return_value = mock_session

        await failure_logger.log_error(
            task_name="test_task",
            platform="linkedin",
            error_type="test_error",
            error_message="Something went wrong",
        )

        # Verify add was called
        mock_session.add.assert_called_once()
        args = mock_session.add.call_args[0]
        db_log = args[0]
        assert isinstance(db_log, DBFailureLog)
        assert db_log.user_id == TEST_USER_ID
        assert db_log.task_name == "test_task"
        assert db_log.error_type == "test_error"

    async def test_get_failure_logs(self, failure_logger, mock_session):
        """Test get_failure_logs retrieves logs."""
        # Mock DB result
        mock_db_log = DBFailureLog(
            id="log-1",
            user_id=TEST_USER_ID,
            task_name="test_task",
            platform="linkedin",
            error_type="test_error",
            error_message="Error",
            created_at=datetime.now(timezone.utc),
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.unique.return_value.all.return_value = [
            mock_db_log
        ]
        mock_session.execute.return_value = mock_result

        logs = await failure_logger.get_failure_logs(user_id=TEST_USER_ID)

        assert len(logs) == 1
        assert logs[0]["id"] == "log-1"
        assert logs[0]["task_name"] == "test_task"

    async def test_cleanup_old_logs(self, failure_logger, mock_session):
        """Test cleanup_old_logs deletes old logs."""
        # Mock execute result for count
        mock_result = MagicMock()
        mock_result.all.return_value = ["log1", "log2"]  # 2 logs found
        mock_session.execute.return_value = mock_result

        # Setup session context manager for begin()
        mock_session.begin.return_value.__aenter__.return_value = mock_session

        count = await failure_logger.cleanup_old_logs()

        assert count == 2
        # Verify execute called twice (select and delete)
        assert mock_session.execute.call_count == 2

    async def test_log_form_filling_error(self, failure_logger, mock_session):
        """Test log_form_filling_error calls log_error with correct type."""
        # Mock log_error to verify calls
        with patch.object(
            failure_logger, "log_error", new_callable=AsyncMock
        ) as mock_log_error:
            await failure_logger.log_form_filling_error(
                platform="linkedin", field_name="email", error_message="Field not found"
            )

            mock_log_error.assert_called_once()
            kwargs = mock_log_error.call_args[1]
            assert kwargs["error_type"] == "form_filling_error"
            assert kwargs["task_name"] == "form_filling"
            assert "field_name" in kwargs["extra"]
