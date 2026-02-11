"""Unit tests for FailureLoggerService."""

import base64
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.failure_logger import FailureLoggerService
from src.database.models import DBFailureLog

TEST_USER_ID = "test-user-123"


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock(return_value=MagicMock())
    session.flush = AsyncMock()
    session.in_transaction = MagicMock(return_value=False)
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

    async def test_log_error_with_screenshot_and_extra(
        self, failure_logger, mock_session
    ):
        """Test log_error encodes screenshot and logs extra context."""
        mock_session.in_transaction = MagicMock(return_value=False)
        mock_session.begin.return_value.__aenter__.return_value = mock_session
        mock_session.flush = AsyncMock()
        failure_logger.logger = MagicMock()
        screenshot = b"binary"
        extra = {"request_id": "req-1"}

        await failure_logger.log_error(
            task_name="test_task",
            platform="linkedin",
            error_type="test_error",
            error_message="Something went wrong",
            screenshot=screenshot,
            extra=extra,
        )

        args = mock_session.add.call_args[0]
        db_log = args[0]
        assert db_log.screenshot == base64.b64encode(screenshot).decode("utf-8")
        failure_logger.logger.debug.assert_called()
        failure_logger.logger.error.assert_called()

    async def test_log_error_uses_existing_transaction(
        self, failure_logger, mock_session
    ):
        """Test log_error uses existing transaction when available."""
        mock_session.in_transaction = MagicMock(return_value=True)
        mock_session.flush = AsyncMock()

        await failure_logger.log_error(
            task_name="test_task",
            platform="linkedin",
            error_type="test_error",
            error_message="Something went wrong",
        )

        mock_session.begin.assert_not_called()

    async def test_log_error_exception_is_caught(self, failure_logger, mock_session):
        """Test log_error handles unexpected exceptions."""
        mock_session.in_transaction = MagicMock(return_value=True)
        mock_session.add.side_effect = Exception("db error")
        failure_logger.logger = MagicMock()

        await failure_logger.log_error(
            task_name="test_task",
            platform="linkedin",
            error_type="test_error",
            error_message="Something went wrong",
        )

        failure_logger.logger.error.assert_called()

    async def test_log_network_error_calls_log_error(self, failure_logger):
        """Test log_network_error forwards to log_error."""
        with patch.object(
            failure_logger, "log_error", new_callable=AsyncMock
        ) as mock_log_error:
            await failure_logger.log_network_error(
                platform="linkedin", error_message="Timeout"
            )

            kwargs = mock_log_error.call_args[1]
            assert kwargs["task_name"] == "network_request"
            assert kwargs["error_type"] == "network_error"

    async def test_log_ai_service_error_calls_log_error(self, failure_logger):
        """Test log_ai_service_error forwards to log_error."""
        with patch.object(
            failure_logger, "log_error", new_callable=AsyncMock
        ) as mock_log_error:
            await failure_logger.log_ai_service_error(
                error_message="AI failed", platform=None
            )

            kwargs = mock_log_error.call_args[1]
            assert kwargs["task_name"] == "ai_service"
            assert kwargs["error_type"] == "ai_service_error"
            assert kwargs["platform"] == "internal"

    async def test_log_rate_limit_error_calls_log_error(self, failure_logger):
        """Test log_rate_limit_error forwards to log_error."""
        with patch.object(
            failure_logger, "log_error", new_callable=AsyncMock
        ) as mock_log_error:
            await failure_logger.log_rate_limit_error(
                platform="linkedin", error_message="Limit reached"
            )

            kwargs = mock_log_error.call_args[1]
            assert kwargs["task_name"] == "rate_limit"
            assert kwargs["error_type"] == "rate_limit_error"

    async def test_get_failure_logs_with_filters(self, failure_logger, mock_session):
        """Test get_failure_logs applies filters and returns results."""
        mock_db_log = DBFailureLog(
            id="log-2",
            user_id=TEST_USER_ID,
            task_name="test_task",
            platform="linkedin",
            error_type="network_error",
            error_message="Error",
            created_at=datetime.now(timezone.utc),
        )
        mock_result = MagicMock()
        mock_result.scalars.return_value.unique.return_value.all.return_value = [
            mock_db_log
        ]
        mock_session.execute.return_value = mock_result

        logs = await failure_logger.get_failure_logs(
            user_id=TEST_USER_ID, platform="linkedin", error_type="network_error"
        )

        assert len(logs) == 1
        assert logs[0]["id"] == "log-2"

    async def test_get_failure_logs_error(self, failure_logger, mock_session):
        """Test get_failure_logs handles errors."""
        mock_session.execute.side_effect = Exception("db error")
        failure_logger.logger = MagicMock()

        logs = await failure_logger.get_failure_logs(user_id=TEST_USER_ID)

        assert logs == []
        failure_logger.logger.error.assert_called()

    async def test_cleanup_old_logs_error(self, failure_logger, mock_session):
        """Test cleanup_old_logs handles errors."""
        mock_session.execute.side_effect = Exception("db error")
        failure_logger.logger = MagicMock()

        count = await failure_logger.cleanup_old_logs()

        assert count == 0
        failure_logger.logger.error.assert_called()

    async def test_get_error_statistics_success(self, failure_logger, mock_session):
        """Test get_error_statistics returns aggregated counts."""
        log_a = MagicMock(error_type="network", platform="linkedin")
        log_b = MagicMock(error_type="network", platform="linkedin")
        log_c = MagicMock(error_type="form", platform="indeed")
        mock_result = MagicMock()
        mock_result.scalars.return_value.unique.return_value.all.return_value = [
            log_a,
            log_b,
            log_c,
        ]
        mock_session.execute.return_value = mock_result

        stats = await failure_logger.get_error_statistics(TEST_USER_ID, days=7)

        assert stats["total_errors"] == 3
        assert stats["by_error_type"]["network"] == 2
        assert stats["by_platform"]["linkedin"] == 2

    async def test_get_error_statistics_error(self, failure_logger, mock_session):
        """Test get_error_statistics handles errors."""
        mock_session.execute.side_effect = Exception("db error")
        failure_logger.logger = MagicMock()

        stats = await failure_logger.get_error_statistics(TEST_USER_ID, days=7)

        assert stats["total_errors"] == 0
        assert stats["by_error_type"] == {}
