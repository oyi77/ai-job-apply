"""Unit tests for CoverLetterService with database."""

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

from src.services.cover_letter_service import CoverLetterService as CoverLetterServiceImpl
from src.core.ai_service import AIService
from src.database.repositories.cover_letter_repository import CoverLetterRepository
from src.database.models import Base
from src.models.cover_letter import CoverLetter, CoverLetterCreate, CoverLetterUpdate


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
async def ai_service():
    """Create a mock AI service."""
    mock_service = AsyncMock(spec=AIService)
    mock_service.is_available.return_value = True
    mock_service.generate_cover_letter.return_value = CoverLetter(
        id="generated-1",
        job_title="Software Engineer",
        company_name="Tech Corp",
        content="Generated cover letter content",
        tone="professional",
        word_count=300,
    )
    return mock_service


@pytest.fixture
async def repository(test_db_session):
    """Create a repository instance."""
    return CoverLetterRepository(test_db_session)


@pytest.fixture
async def service(ai_service, repository):
    """Create a service instance with repository."""
    return CoverLetterServiceImpl(ai_service, repository)


@pytest.mark.asyncio
async def test_create_cover_letter_with_repository(service):
    """Test creating a cover letter with database repository."""
    cover_letter_data = CoverLetterCreate(
        job_title="Software Engineer",
        company_name="Tech Corp",
        content="Dear Hiring Manager...",
        tone="professional",
        word_count=300,
    )
    
    result = await service.create_cover_letter(cover_letter_data)
    
    assert result is not None
    assert result.job_title == "Software Engineer"
    assert result.company_name == "Tech Corp"
    assert result.content == "Dear Hiring Manager..."


@pytest.mark.asyncio
async def test_get_all_cover_letters_with_repository(service):
    """Test getting all cover letters with database repository."""
    cl1_data = CoverLetterCreate(
        job_title="Engineer 1",
        company_name="Corp 1",
        content="Content 1",
        tone="professional",
        word_count=300,
    )
    cl2_data = CoverLetterCreate(
        job_title="Engineer 2",
        company_name="Corp 2",
        content="Content 2",
        tone="professional",
        word_count=300,
    )
    
    await service.create_cover_letter(cl1_data)
    await service.create_cover_letter(cl2_data)
    
    results = await service.get_all_cover_letters()
    
    assert len(results) == 2
    assert any(cl.job_title == "Engineer 1" for cl in results)
    assert any(cl.job_title == "Engineer 2" for cl in results)


@pytest.mark.asyncio
async def test_get_cover_letter_with_repository(service):
    """Test getting a cover letter by ID with database repository."""
    cover_letter_data = CoverLetterCreate(
        job_title="Software Engineer",
        company_name="Tech Corp",
        content="Dear Hiring Manager...",
        tone="professional",
        word_count=300,
    )
    
    created = await service.create_cover_letter(cover_letter_data)
    retrieved = await service.get_cover_letter(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.job_title == "Software Engineer"


@pytest.mark.asyncio
async def test_update_cover_letter_with_repository(service):
    """Test updating a cover letter with database repository."""
    cover_letter_data = CoverLetterCreate(
        job_title="Software Engineer",
        company_name="Tech Corp",
        content="Original content",
        tone="professional",
        word_count=300,
    )
    
    created = await service.create_cover_letter(cover_letter_data)
    
    updates = CoverLetterUpdate(
        content="Updated content",
        tone="casual",
    )
    
    updated = await service.update_cover_letter(created.id, updates)
    
    assert updated is not None
    assert updated.content == "Updated content"
    assert updated.tone == "casual"
    assert updated.id == created.id


@pytest.mark.asyncio
async def test_delete_cover_letter_with_repository(service):
    """Test deleting a cover letter with database repository."""
    cover_letter_data = CoverLetterCreate(
        job_title="Software Engineer",
        company_name="Tech Corp",
        content="Dear Hiring Manager...",
        tone="professional",
        word_count=300,
    )
    
    created = await service.create_cover_letter(cover_letter_data)
    
    success = await service.delete_cover_letter(created.id)
    
    assert success is True
    
    # Verify cover letter is no longer in database
    deleted = await service.get_cover_letter(created.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_generate_cover_letter_with_ai(service, ai_service):
    """Test generating a cover letter using AI with database repository."""
    generated = await service.generate_cover_letter(
        job_title="Software Engineer",
        company_name="Tech Corp",
        job_description="Python development position",
        resume_summary="5 years of Python experience",
        tone="professional"
    )
    
    assert generated is not None
    assert generated.job_title == "Software Engineer"
    assert generated.company_name == "Tech Corp"
    assert ai_service.generate_cover_letter.called


@pytest.mark.asyncio
async def test_generate_cover_letter_fallback_template(service, ai_service):
    """Test generating a cover letter with template fallback."""
    ai_service.is_available.return_value = False
    
    generated = await service.generate_cover_letter(
        job_title="Software Engineer",
        company_name="Tech Corp",
        job_description="Python development position",
        resume_summary="5 years of Python experience",
        tone="professional"
    )
    
    assert generated is not None
    assert generated.job_title == "Software Engineer"
    assert generated.company_name == "Tech Corp"
    assert "Tech Corp" in generated.content


@pytest.mark.asyncio
async def test_get_cover_letter_not_found(service):
    """Test getting a non-existent cover letter."""
    result = await service.get_cover_letter("nonexistent-id")
    assert result is None


@pytest.mark.asyncio
async def test_update_cover_letter_not_found(service):
    """Test updating a non-existent cover letter."""
    updates = CoverLetterUpdate(content="Updated content")
    result = await service.update_cover_letter("nonexistent-id", updates)
    assert result is None


@pytest.mark.asyncio
async def test_delete_cover_letter_not_found(service):
    """Test deleting a non-existent cover letter."""
    result = await service.delete_cover_letter("nonexistent-id")
    assert result is False


@pytest.mark.asyncio
async def test_health_check_with_repository(service):
    """Test health check with database repository."""
    await service.create_cover_letter(CoverLetterCreate(
        job_title="Test",
        company_name="Test Corp",
        content="Test content",
        tone="professional",
        word_count=300,
    ))
    
    health = await service.health_check()
    
    assert health["status"] == "healthy"
    assert health["available"] is True
    assert health["cover_letter_count"] == 1
    assert health["ai_service_available"] is True
    assert health["using_database"] is True

