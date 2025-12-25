"""Unit tests for CoverLetterService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.services.cover_letter_service import CoverLetterService
from src.models.cover_letter import CoverLetter, CoverLetterCreate, CoverLetterUpdate
from src.core.cover_letter_service import CoverLetterService as ICoverLetterService


@pytest.fixture
def mock_ai_service():
    """Create a mock AI service."""
    mock = AsyncMock()
    from datetime import timezone
    mock.generate_cover_letter.return_value = CoverLetter(
        id="test-id",
        job_title="Software Engineer",
        company_name="Tech Corp",
        content="Generated cover letter content",
        tone="professional",
        word_count=250,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    return mock


@pytest.fixture
def cover_letter_service(mock_ai_service):
    """Create CoverLetterService instance."""
    return CoverLetterService(ai_service=mock_ai_service)


@pytest.mark.asyncio
async def test_get_all_cover_letters_empty(cover_letter_service):
    """Test getting all cover letters when none exist."""
    cover_letters = await cover_letter_service.get_all_cover_letters()
    assert isinstance(cover_letters, list)
    assert len(cover_letters) == 0


@pytest.mark.asyncio
async def test_create_cover_letter(cover_letter_service):
    """Test creating a cover letter."""
    create_data = CoverLetterCreate(
        job_title="Software Engineer",
        company_name="Tech Corp",
        content="Test content",
        tone="professional"
    )
    
    cover_letter = await cover_letter_service.create_cover_letter(create_data)
    
    assert cover_letter.job_title == "Software Engineer"
    assert cover_letter.company_name == "Tech Corp"
    assert cover_letter.content == "Test content"
    assert cover_letter.id is not None


@pytest.mark.asyncio
async def test_get_cover_letter_by_id(cover_letter_service):
    """Test getting a cover letter by ID."""
    create_data = CoverLetterCreate(
        job_title="Engineer",
        company_name="Corp",
        content="Content"
    )
    
    created = await cover_letter_service.create_cover_letter(create_data)
    retrieved = await cover_letter_service.get_cover_letter(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.job_title == "Engineer"


@pytest.mark.asyncio
async def test_get_cover_letter_not_found(cover_letter_service):
    """Test getting a non-existent cover letter."""
    result = await cover_letter_service.get_cover_letter("non-existent-id")
    assert result is None


@pytest.mark.asyncio
async def test_update_cover_letter(cover_letter_service):
    """Test updating a cover letter."""
    create_data = CoverLetterCreate(
        job_title="Engineer",
        company_name="Corp",
        content="Original content"
    )
    
    created = await cover_letter_service.create_cover_letter(create_data)
    
    update_data = CoverLetterUpdate(
        content="Updated content"
    )
    
    updated = await cover_letter_service.update_cover_letter(created.id, update_data)
    
    assert updated is not None
    assert updated.content == "Updated content"
    assert updated.id == created.id


@pytest.mark.asyncio
async def test_delete_cover_letter(cover_letter_service):
    """Test deleting a cover letter."""
    create_data = CoverLetterCreate(
        job_title="Engineer",
        company_name="Corp",
        content="Content"
    )
    
    created = await cover_letter_service.create_cover_letter(create_data)
    result = await cover_letter_service.delete_cover_letter(created.id)
    
    assert result is True
    
    # Verify it's deleted
    retrieved = await cover_letter_service.get_cover_letter(created.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_generate_cover_letter_with_ai(cover_letter_service, mock_ai_service):
    """Test generating a cover letter using AI."""
    create_data = CoverLetterCreate(
        job_title="Software Engineer",
        company_name="Tech Corp",
        content="",
        tone="professional"
    )
    
    # Pass individual arguments as per the new signature
    generated = await cover_letter_service.generate_cover_letter(
        job_title=create_data.job_title,
        company_name=create_data.company_name,
        job_description="Python developer position",
        resume_summary="Experienced developer",
        tone=create_data.tone
    )
    
    assert generated is not None
    assert generated.job_title == "Software Engineer"
    assert generated.company_name == "Tech Corp"
    assert len(generated.content) > 0
    mock_ai_service.generate_cover_letter.assert_called_once()

