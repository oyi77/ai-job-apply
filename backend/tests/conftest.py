"""Pytest configuration and fixtures for the AI Job Application Assistant."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
import shutil
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest

import sys
from pathlib import Path

# Ensure `src` package is importable when running tests without installing the
# project into the current environment.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
TESTS_ROOT = Path(__file__).resolve().parents[0]

# Add paths in order: project root first, then tests for fixtures, then src
paths_to_add = [
    str(PROJECT_ROOT),
    str(TESTS_ROOT),
    str(SRC_ROOT),
]

for p in paths_to_add:
    if p not in sys.path:
        sys.path.insert(0, p)

# Now imports will work
from fixtures.test_data import (  # noqa: E402
    sample_application_data,
    sample_cover_letter_data,
    sample_job_data,
    sample_resume_data,
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
        "mime_type": "application/pdf",
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


@pytest.fixture
async def test_user_2(client):
    """Register and return a second test user."""
    user_data = {
        "email": f"user2_{uuid.uuid4()}@example.com",
        "password": "Password123!",
        "name": "User Two",
    }
    # Note: validation of response status should be done in tests
    # But usually fixtures should guarantee success or fail
    response = await client.post("/api/v1/auth/register", json=user_data)
    if response.status_code == 400 and "already registered" in response.text:
        # Try login
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )

    if response.status_code not in [200, 201]:
        # Return basic data if registration fails (e.g. if client is mocked without auth logic)
        return user_data

    return response.json()


@pytest.fixture
def test_user_2_token(test_user_2):
    """Return the access token for test_user_2."""
    if isinstance(test_user_2, dict):
        return test_user_2.get("access_token")
    return None
