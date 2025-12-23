"""Unit tests for ApplicationService with database."""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, MagicMock
import sys

# Mock dependencies before importing services
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['PyPDF2'] = MagicMock()
sys.modules['docx'] = MagicMock()

from src.services.application_service import ApplicationService
from src.services.local_file_service import LocalFileService
from src.database.repositories.application_repository import ApplicationRepository
from src.database.models import Base
from src.models.application import JobApplication, ApplicationStatus


@pytest.fixture
async def test_db_session():
    """Create a test database session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
async def file_service():
    """Create a mock file service."""
    mock_service = AsyncMock(spec=LocalFileService)
    return mock_service


@pytest.fixture
async def repository(test_db_session):
    """Create a repository instance."""
    return ApplicationRepository(test_db_session)


@pytest.fixture
async def service(file_service, repository):
    """Create a service instance with repository."""
    return ApplicationService(file_service, repository)


@pytest.mark.asyncio
async def test_create_application_with_repository(service):
    """Test creating an application with database repository."""
    job_info = {
        "job_id": "job-1",
        "job_title": "Test Developer",
        "company": "Test Corp",
        "location": "Remote",
        "status": ApplicationStatus.DRAFT,
    }
    
    result = await service.create_application(job_info)
    
    assert result is not None
    assert result.job_title == "Test Developer"
    assert result.company == "Test Corp"


@pytest.mark.asyncio
async def test_get_all_applications_with_repository(service):
    """Test getting all applications with database repository."""
    job_info1 = {
        "job_id": "job-1",
        "job_title": "Developer 1",
        "company": "Corp 1",
    }
    job_info2 = {
        "job_id": "job-2",
        "job_title": "Developer 2",
        "company": "Corp 2",
    }
    
    await service.create_application(job_info1)
    await service.create_application(job_info2)
    
    results = await service.get_all_applications()
    
    assert len(results) == 2


@pytest.mark.asyncio
async def test_get_application_stats_with_repository(service):
    """Test getting application statistics with database repository."""
    job_info1 = {
        "job_id": "job-1",
        "job_title": "Developer 1",
        "company": "Corp 1",
        "status": ApplicationStatus.DRAFT,
    }
    job_info2 = {
        "job_id": "job-2",
        "job_title": "Developer 2",
        "company": "Corp 2",
        "status": ApplicationStatus.SUBMITTED,
    }
    
    await service.create_application(job_info1)
    await service.create_application(job_info2)
    
    stats = await service.get_application_stats()
    
    assert stats["total_applications"] == 2
    assert "status_breakdown" in stats

