"""Unit tests for resume service."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from src.services.file_based_resume_service import FileBasedResumeService
from src.models.resume import Resume


class TestFileBasedResumeService:
    """Test cases for FileBasedResumeService."""
    
    @pytest.fixture
    def mock_file_service(self):
        """Mock file service for testing."""
        mock_service = AsyncMock()
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
    def resume_service(self, mock_file_service):
        """Create resume service with mocked dependencies."""
        return FileBasedResumeService(file_service=mock_file_service)
    
    @pytest.mark.asyncio
    async def test_upload_resume_success(self, resume_service, mock_file_service):
        """Test successful resume upload."""
        file_path = "/test/resume.pdf"
        name = "Test Resume"
        
        # Mock text extraction
        resume_service.extract_text_from_file = AsyncMock(return_value="Software Engineer with 5 years experience")
        
        # Upload resume
        resume = await resume_service.upload_resume(file_path, name)
        
        # Assertions
        assert resume is not None
        assert resume.name == name
        assert resume.file_path == file_path
        assert resume.file_type == "pdf"
        assert resume.is_default is True  # First resume should be default
        
        # Verify file service calls
        mock_file_service.file_exists.assert_called_once_with(file_path)
        mock_file_service.get_file_info.assert_called_once_with(file_path)
    
    @pytest.mark.asyncio
    async def test_upload_resume_file_not_found(self, resume_service, mock_file_service):
        """Test resume upload with non-existent file."""
        mock_file_service.file_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            await resume_service.upload_resume("/nonexistent/file.pdf", "Test Resume")
    
    @pytest.mark.asyncio
    async def test_upload_resume_invalid_file_type(self, resume_service, mock_file_service):
        """Test resume upload with invalid file type."""
        mock_file_service.is_valid_file_type.return_value = False
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            await resume_service.upload_resume("/test/resume.exe", "Test Resume")
    
    @pytest.mark.asyncio
    async def test_get_resume_success(self, resume_service):
        """Test successful resume retrieval."""
        # First upload a resume
        resume_service.extract_text_from_file = AsyncMock(return_value="test content")
        uploaded_resume = await resume_service.upload_resume("/test/resume.pdf", "Test Resume")
        
        # Get the resume
        retrieved_resume = await resume_service.get_resume(uploaded_resume.id)
        
        # Assertions
        assert retrieved_resume is not None
        assert retrieved_resume.id == uploaded_resume.id
        assert retrieved_resume.name == "Test Resume"
    
    @pytest.mark.asyncio
    async def test_get_resume_not_found(self, resume_service):
        """Test resume retrieval with non-existent ID."""
        result = await resume_service.get_resume("nonexistent-id")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_all_resumes(self, resume_service):
        """Test getting all resumes."""
        # Upload multiple resumes
        resume_service.extract_text_from_file = AsyncMock(return_value="test content")
        
        resume1 = await resume_service.upload_resume("/test/resume1.pdf", "Resume 1")
        resume2 = await resume_service.upload_resume("/test/resume2.pdf", "Resume 2")
        
        # Get all resumes
        all_resumes = await resume_service.get_all_resumes()
        
        # Assertions
        assert len(all_resumes) == 2
        assert all_resumes[0].name in ["Resume 1", "Resume 2"]
        assert all_resumes[1].name in ["Resume 1", "Resume 2"]
    
    @pytest.mark.asyncio
    async def test_set_default_resume(self, resume_service):
        """Test setting a resume as default."""
        # Upload two resumes
        resume_service.extract_text_from_file = AsyncMock(return_value="test content")
        
        resume1 = await resume_service.upload_resume("/test/resume1.pdf", "Resume 1")
        resume2 = await resume_service.upload_resume("/test/resume2.pdf", "Resume 2")
        
        # Initially, first resume should be default
        assert resume1.is_default is True
        assert resume2.is_default is False
        
        # Set second resume as default
        success = await resume_service.set_default_resume(resume2.id)
        
        # Assertions
        assert success is True
        assert resume1.is_default is False
        assert resume2.is_default is True
    
    @pytest.mark.asyncio
    async def test_delete_resume(self, resume_service, mock_file_service):
        """Test resume deletion."""
        # Upload a resume
        resume_service.extract_text_from_file = AsyncMock(return_value="test content")
        resume = await resume_service.upload_resume("/test/resume.pdf", "Test Resume")
        
        # Delete the resume
        success = await resume_service.delete_resume(resume.id)
        
        # Assertions
        assert success is True
        mock_file_service.delete_file.assert_called_once_with("/test/resume.pdf")
        
        # Verify resume is no longer in storage
        deleted_resume = await resume_service.get_resume(resume.id)
        assert deleted_resume is None
    
    @pytest.mark.asyncio
    async def test_update_resume(self, resume_service):
        """Test resume update."""
        # Upload a resume
        resume_service.extract_text_from_file = AsyncMock(return_value="test content")
        resume = await resume_service.upload_resume("/test/resume.pdf", "Original Name")
        
        # Update the resume
        updates = {"name": "Updated Name"}
        updated_resume = await resume_service.update_resume(resume.id, updates)
        
        # Assertions
        assert updated_resume is not None
        assert updated_resume.name == "Updated Name"
        assert updated_resume.id == resume.id
    
    def test_estimate_experience_years(self, resume_service):
        """Test experience years estimation."""
        content = "I have 5 years of experience in software development"
        years = resume_service._estimate_experience_years(content)
        assert years == 5
        
        content_no_experience = "I am a recent graduate"
        years = resume_service._estimate_experience_years(content_no_experience)
        assert years is None
    
    def test_extract_education(self, resume_service):
        """Test education extraction."""
        content = "Bachelor of Science in Computer Science from MIT University"
        education = resume_service._extract_education(content)
        assert education is not None
        assert len(education) > 0
        assert any("bachelor" in edu.lower() for edu in education)
    
    def test_extract_certifications(self, resume_service):
        """Test certifications extraction."""
        content = "AWS Certified Developer, Microsoft Certified Azure Developer"
        certifications = resume_service._extract_certifications(content)
        assert certifications is not None
        assert len(certifications) > 0
        assert any("aws certified" in cert.lower() for cert in certifications)
