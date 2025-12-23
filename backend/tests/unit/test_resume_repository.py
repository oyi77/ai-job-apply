"""Unit tests for ResumeRepository."""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.repositories.resume_repository import ResumeRepository
from src.database.models import DBResume, Base
from src.models.resume import Resume


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
    return ResumeRepository(test_db_session)


@pytest.mark.asyncio
async def test_create_resume(repository):
    """Test creating a resume."""
    resume = Resume(
        id="test-1",
        name="Test Resume",
        file_path="/test/resume.pdf",
        file_type="pdf",
        content="Test content",
        skills=["Python", "JavaScript"],
        is_default=False,
    )
    
    result = await repository.create(resume)
    
    assert result.id == resume.id
    assert result.name == "Test Resume"
    assert result.file_type == "pdf"


@pytest.mark.asyncio
async def test_get_by_id(repository):
    """Test getting resume by ID."""
    resume = Resume(
        id="test-1",
        name="Test Resume",
        file_path="/test/resume.pdf",
        file_type="pdf",
        content="Test content",
    )
    
    await repository.create(resume)
    result = await repository.get_by_id("test-1")
    
    assert result is not None
    assert result.name == "Test Resume"


@pytest.mark.asyncio
async def test_get_all(repository):
    """Test getting all resumes."""
    resume1 = Resume(
        id="test-1",
        name="Resume 1",
        file_path="/test/resume1.pdf",
        file_type="pdf",
        content="Content 1",
    )
    resume2 = Resume(
        id="test-2",
        name="Resume 2",
        file_path="/test/resume2.pdf",
        file_type="pdf",
        content="Content 2",
    )
    
    await repository.create(resume1)
    await repository.create(resume2)
    
    results = await repository.get_all()
    
    assert len(results) == 2


@pytest.mark.asyncio
async def test_set_default_resume(repository):
    """Test setting default resume."""
    resume1 = Resume(
        id="test-1",
        name="Resume 1",
        file_path="/test/resume1.pdf",
        file_type="pdf",
        content="Content 1",
        is_default=True,
    )
    resume2 = Resume(
        id="test-2",
        name="Resume 2",
        file_path="/test/resume2.pdf",
        file_type="pdf",
        content="Content 2",
        is_default=False,
    )
    
    await repository.create(resume1)
    await repository.create(resume2)
    
    result = await repository.set_default_resume("test-2")
    
    assert result is True
    
    default = await repository.get_default_resume()
    assert default is not None
    assert default.id == "test-2"


@pytest.mark.asyncio
async def test_update_resume(repository):
    """Test updating a resume."""
    resume = Resume(
        id="test-1",
        name="Test Resume",
        file_path="/test/resume.pdf",
        file_type="pdf",
        content="Test content",
    )
    
    await repository.create(resume)
    
    result = await repository.update("test-1", {"name": "Updated Resume"})
    
    assert result is not None
    assert result.name == "Updated Resume"


@pytest.mark.asyncio
async def test_delete_resume(repository):
    """Test deleting a resume."""
    resume = Resume(
        id="test-1",
        name="Test Resume",
        file_path="/test/resume.pdf",
        file_type="pdf",
        content="Test content",
    )
    
    await repository.create(resume)
    
    result = await repository.delete("test-1")
    
    assert result is True
    
    deleted = await repository.get_by_id("test-1")
    assert deleted is None

