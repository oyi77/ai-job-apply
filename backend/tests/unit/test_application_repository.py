"""Unit tests for ApplicationRepository."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.repositories.application_repository import ApplicationRepository
from src.database.models import DBJobApplication, Base
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
async def repository(test_db_session):
    """Create a repository instance."""
    return ApplicationRepository(test_db_session)


@pytest.mark.asyncio
async def test_create_application(repository):
    """Test creating an application."""
    application = JobApplication(
        id="test-1",
        job_id="job-1",
        job_title="Test Developer",
        company="Test Corp",
        location="Remote",
        status=ApplicationStatus.DRAFT,
    )
    
    result = await repository.create(application)
    
    assert result.id == application.id
    assert result.job_title == "Test Developer"
    assert result.company == "Test Corp"


@pytest.mark.asyncio
async def test_get_by_id(repository):
    """Test getting application by ID."""
    application = JobApplication(
        id="test-1",
        job_id="job-1",
        job_title="Test Developer",
        company="Test Corp",
        status=ApplicationStatus.DRAFT,
    )
    
    await repository.create(application)
    result = await repository.get_by_id("test-1")
    
    assert result is not None
    assert result.job_title == "Test Developer"


@pytest.mark.asyncio
async def test_get_all(repository):
    """Test getting all applications."""
    app1 = JobApplication(
        id="test-1",
        job_id="job-1",
        job_title="Developer 1",
        company="Corp 1",
        status=ApplicationStatus.DRAFT,
    )
    app2 = JobApplication(
        id="test-2",
        job_id="job-2",
        job_title="Developer 2",
        company="Corp 2",
        status=ApplicationStatus.SUBMITTED,
    )
    
    await repository.create(app1)
    await repository.create(app2)
    
    results = await repository.get_all()
    
    assert len(results) == 2


@pytest.mark.asyncio
async def test_get_by_status(repository):
    """Test getting applications by status."""
    app1 = JobApplication(
        id="test-1",
        job_id="job-1",
        job_title="Developer 1",
        company="Corp 1",
        status=ApplicationStatus.DRAFT,
    )
    app2 = JobApplication(
        id="test-2",
        job_id="job-2",
        job_title="Developer 2",
        company="Corp 2",
        status=ApplicationStatus.SUBMITTED,
    )
    
    await repository.create(app1)
    await repository.create(app2)
    
    results = await repository.get_by_status(ApplicationStatus.DRAFT)
    
    assert len(results) == 1
    assert results[0].status == ApplicationStatus.DRAFT


@pytest.mark.asyncio
async def test_update_application(repository):
    """Test updating an application."""
    application = JobApplication(
        id="test-1",
        job_id="job-1",
        job_title="Test Developer",
        company="Test Corp",
        status=ApplicationStatus.DRAFT,
    )
    
    await repository.create(application)
    
    from src.models.application import ApplicationUpdateRequest
    updates = ApplicationUpdateRequest(status=ApplicationStatus.SUBMITTED)
    
    result = await repository.update("test-1", updates)
    
    assert result is not None
    assert result.status == ApplicationStatus.SUBMITTED


@pytest.mark.asyncio
async def test_delete_application(repository):
    """Test deleting an application."""
    application = JobApplication(
        id="test-1",
        job_id="job-1",
        job_title="Test Developer",
        company="Test Corp",
        status=ApplicationStatus.DRAFT,
    )
    
    await repository.create(application)
    
    result = await repository.delete("test-1")
    
    assert result is True
    
    deleted = await repository.get_by_id("test-1")
    assert deleted is None


@pytest.mark.asyncio
async def test_get_statistics(repository):
    """Test getting application statistics."""
    app1 = JobApplication(
        id="test-1",
        job_id="job-1",
        job_title="Developer 1",
        company="Corp 1",
        status=ApplicationStatus.DRAFT,
    )
    app2 = JobApplication(
        id="test-2",
        job_id="job-2",
        job_title="Developer 2",
        company="Corp 2",
        status=ApplicationStatus.SUBMITTED,
        applied_date=datetime.utcnow(),
    )
    
    await repository.create(app1)
    await repository.create(app2)
    
    stats = await repository.get_statistics()
    
    assert stats["total_applications"] == 2
    assert ApplicationStatus.DRAFT in stats["status_breakdown"]
    assert ApplicationStatus.SUBMITTED in stats["status_breakdown"]

