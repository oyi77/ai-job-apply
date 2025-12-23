"""Unit tests for ResumeService with database."""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, MagicMock, patch
import sys

# Mock dependencies before importing services
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['PyPDF2'] = MagicMock()
sys.modules['docx'] = MagicMock()

from src.services.resume_service import ResumeService as ResumeServiceImpl
from src.services.local_file_service import LocalFileService
from src.database.repositories.resume_repository import ResumeRepository
from src.database.models import Base
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
async def file_service():
    """Create a mock file service."""
    mock_service = AsyncMock(spec=LocalFileService)
    mock_service.file_exists.return_value = True
    mock_service.get_file_info.return_value = {
        "name": "test_resume.pdf",
        "size": 1024,
        "extension": ".pdf",
        "mime_type": "application/pdf"
    }
    mock_service.is_valid_file_type.return_value = True
    mock_service.get_file_size.return_value = 1024
    mock_service.read_file.return_value = b"test resume content"
    return mock_service


@pytest.fixture
async def repository(test_db_session):
    """Create a repository instance."""
    return ResumeRepository(test_db_session)


@pytest.fixture
async def service(file_service, repository):
    """Create a service instance with repository."""
    service = ResumeServiceImpl(file_service, repository)
    # Mock text extraction
    service.extract_text_from_file = AsyncMock(return_value="Software Engineer with 5 years experience")
    return service


@pytest.mark.asyncio
async def test_upload_resume_with_repository(service):
    """Test uploading a resume with database repository."""
    file_path = "/test/resume.pdf"
    name = "Test Resume"
    
    result = await service.upload_resume(file_path, name)
    
    assert result is not None
    assert result.name == name
    assert result.file_path == file_path
    assert result.file_type == "pdf"
    assert result.is_default is True  # First resume should be default


@pytest.mark.asyncio
async def test_get_all_resumes_with_repository(service):
    """Test getting all resumes with database repository."""
    # Upload multiple resumes
    resume1 = await service.upload_resume("/test/resume1.pdf", "Resume 1")
    resume2 = await service.upload_resume("/test/resume2.pdf", "Resume 2")
    
    results = await service.get_all_resumes()
    
    assert len(results) == 2
    assert any(r.name == "Resume 1" for r in results)
    assert any(r.name == "Resume 2" for r in results)


@pytest.mark.asyncio
async def test_get_resume_with_repository(service):
    """Test getting a resume by ID with database repository."""
    uploaded_resume = await service.upload_resume("/test/resume.pdf", "Test Resume")
    
    retrieved_resume = await service.get_resume(uploaded_resume.id)
    
    assert retrieved_resume is not None
    assert retrieved_resume.id == uploaded_resume.id
    assert retrieved_resume.name == "Test Resume"


@pytest.mark.asyncio
async def test_set_default_resume_with_repository(service):
    """Test setting default resume with database repository."""
    resume1 = await service.upload_resume("/test/resume1.pdf", "Resume 1")
    resume2 = await service.upload_resume("/test/resume2.pdf", "Resume 2")
    
    # Initially, first resume should be default
    default1 = await service.get_default_resume()
    assert default1.id == resume1.id
    
    # Set second resume as default
    success = await service.set_default_resume(resume2.id)
    
    assert success is True
    default2 = await service.get_default_resume()
    assert default2.id == resume2.id


@pytest.mark.asyncio
async def test_update_resume_with_repository(service):
    """Test updating a resume with database repository."""
    resume = await service.upload_resume("/test/resume.pdf", "Original Name")
    
    updates = {"name": "Updated Name"}
    updated_resume = await service.update_resume(resume.id, updates)
    
    assert updated_resume is not None
    assert updated_resume.name == "Updated Name"
    assert updated_resume.id == resume.id


@pytest.mark.asyncio
async def test_delete_resume_with_repository(service, file_service):
    """Test deleting a resume with database repository."""
    resume = await service.upload_resume("/test/resume.pdf", "Test Resume")
    
    success = await service.delete_resume(resume.id)
    
    assert success is True
    file_service.delete_file.assert_called_once_with("/test/resume.pdf")
    
    # Verify resume is no longer in database
    deleted_resume = await service.get_resume(resume.id)
    assert deleted_resume is None


@pytest.mark.asyncio
async def test_get_default_resume_with_repository(service):
    """Test getting default resume with database repository."""
    # No resumes yet
    default = await service.get_default_resume()
    assert default is None
    
    # Upload first resume
    resume1 = await service.upload_resume("/test/resume1.pdf", "Resume 1")
    default = await service.get_default_resume()
    assert default is not None
    assert default.id == resume1.id


@pytest.mark.asyncio
async def test_upload_resume_file_not_found(service, file_service):
    """Test resume upload with non-existent file."""
    file_service.file_exists.return_value = False
    
    with pytest.raises(FileNotFoundError):
        await service.upload_resume("/nonexistent/file.pdf", "Test Resume")


@pytest.mark.asyncio
async def test_upload_resume_invalid_file_type(service, file_service):
    """Test resume upload with invalid file type."""
    file_service.is_valid_file_type.return_value = False
    
    with pytest.raises(ValueError, match="Unsupported file type"):
        await service.upload_resume("/test/resume.exe", "Test Resume")


@pytest.mark.asyncio
async def test_health_check_with_repository(service):
    """Test health check with database repository."""
    await service.upload_resume("/test/resume.pdf", "Test Resume")
    
    health = await service.health_check()
    
    assert health["status"] == "healthy"
    assert health["available"] is True
    assert health["resume_count"] == 1
    assert health["default_resume"] is True
    assert health["using_database"] is True

