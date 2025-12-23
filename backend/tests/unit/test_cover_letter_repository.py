"""Unit tests for CoverLetterRepository."""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.repositories.cover_letter_repository import CoverLetterRepository
from src.database.models import DBCoverLetter, Base
from src.models.cover_letter import CoverLetter


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
    return CoverLetterRepository(test_db_session)


@pytest.mark.asyncio
async def test_create_cover_letter(repository):
    """Test creating a cover letter."""
    cover_letter = CoverLetter(
        id="test-1",
        job_title="Software Engineer",
        company_name="Tech Corp",
        content="Dear Hiring Manager...",
        tone="professional",
        word_count=300,
    )
    
    result = await repository.create(cover_letter)
    
    assert result.id == cover_letter.id
    assert result.job_title == "Software Engineer"
    assert result.company_name == "Tech Corp"


@pytest.mark.asyncio
async def test_get_by_id(repository):
    """Test getting cover letter by ID."""
    cover_letter = CoverLetter(
        id="test-1",
        job_title="Software Engineer",
        company_name="Tech Corp",
        content="Dear Hiring Manager...",
        tone="professional",
        word_count=300,
    )
    
    await repository.create(cover_letter)
    result = await repository.get_by_id("test-1")
    
    assert result is not None
    assert result.job_title == "Software Engineer"


@pytest.mark.asyncio
async def test_get_all(repository):
    """Test getting all cover letters."""
    cl1 = CoverLetter(
        id="test-1",
        job_title="Engineer 1",
        company_name="Corp 1",
        content="Content 1",
        tone="professional",
        word_count=300,
    )
    cl2 = CoverLetter(
        id="test-2",
        job_title="Engineer 2",
        company_name="Corp 2",
        content="Content 2",
        tone="professional",
        word_count=300,
    )
    
    await repository.create(cl1)
    await repository.create(cl2)
    
    results = await repository.get_all()
    
    assert len(results) == 2


@pytest.mark.asyncio
async def test_update_cover_letter(repository):
    """Test updating a cover letter."""
    cover_letter = CoverLetter(
        id="test-1",
        job_title="Software Engineer",
        company_name="Tech Corp",
        content="Dear Hiring Manager...",
        tone="professional",
        word_count=300,
    )
    
    await repository.create(cover_letter)
    
    result = await repository.update("test-1", {"content": "Updated content"})
    
    assert result is not None
    assert result.content == "Updated content"


@pytest.mark.asyncio
async def test_delete_cover_letter(repository):
    """Test deleting a cover letter."""
    cover_letter = CoverLetter(
        id="test-1",
        job_title="Software Engineer",
        company_name="Tech Corp",
        content="Dear Hiring Manager...",
        tone="professional",
        word_count=300,
    )
    
    await repository.create(cover_letter)
    
    result = await repository.delete("test-1")
    
    assert result is True
    
    deleted = await repository.get_by_id("test-1")
    assert deleted is None

