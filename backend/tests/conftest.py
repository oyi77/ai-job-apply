"""Pytest configuration and fixtures for the AI Job Application Assistant."""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
import tempfile
import shutil
from pathlib import Path

# Import test fixtures and utilities
from .fixtures.test_data import (
    sample_resume_data,
    sample_application_data,
    sample_job_data,
    sample_cover_letter_data
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def temp_directory() -> AsyncGenerator[Path, None]:
    """Create a temporary directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing."""
    mock_service = AsyncMock()
    mock_service.is_available.return_value = True
    mock_service.optimize_resume.return_value = MagicMock()
    mock_service.generate_cover_letter.return_value = MagicMock()
    return mock_service


@pytest.fixture
def mock_file_service():
    """Mock file service for testing."""
    mock_service = AsyncMock()
    mock_service.save_file.return_value = True
    mock_service.read_file.return_value = b"test file content"
    mock_service.file_exists.return_value = True
    mock_service.delete_file.return_value = True
    mock_service.get_file_info.return_value = {
        "name": "test.pdf",
        "size": 1024,
        "extension": ".pdf",
        "mime_type": "application/pdf"
    }
    return mock_service


@pytest.fixture
def sample_resume():
    """Sample resume data for testing."""
    return sample_resume_data()


@pytest.fixture
def sample_application():
    """Sample application data for testing."""
    return sample_application_data()


@pytest.fixture
def sample_job():
    """Sample job data for testing."""
    return sample_job_data()


@pytest.fixture
def sample_cover_letter():
    """Sample cover letter data for testing."""
    return sample_cover_letter_data()


@pytest.fixture
async def mock_database():
    """Mock database for testing."""
    # This would be replaced with actual test database setup
    return AsyncMock()


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    config = MagicMock()
    config.MAX_FILE_SIZE_MB = 10
    config.UPLOAD_DIRECTORY = "test_uploads"
    config.GEMINI_API_KEY = "test_api_key"
    config.DATABASE_URL = "sqlite:///test.db"
    return config
