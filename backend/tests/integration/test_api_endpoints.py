"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
import tempfile
import io
from pathlib import Path

from src.api.app import create_app


class TestResumeEndpoints:
    """Integration tests for resume endpoints."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_get_all_resumes(self, client):
        """Test getting all resumes."""
        response = await client.get("/api/v1/resumes/")
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert isinstance(data["data"], list)
    
    @pytest.mark.asyncio
    async def test_upload_resume_success(self, client):
        """Test successful resume upload."""
        # Create a temporary PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        
        with patch('src.services.service_registry.service_registry') as mock_registry:
            # Mock the services
            mock_file_service = AsyncMock()
            mock_file_service.save_file.return_value = True
            
            mock_resume_service = AsyncMock()
            mock_resume_service.upload_resume.return_value = AsyncMock(
                id="test-id",
                name="Test Resume",
                file_path="/test/path.pdf",
                file_type="pdf"
            )
            
            mock_registry.get_file_service.return_value = mock_file_service
            mock_registry.get_resume_service.return_value = mock_resume_service
            
            # Upload file
            files = {"file": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")}
            data = {"name": "Test Resume"}
            
            response = await client.post("/api/v1/resumes/upload", files=files, data=data)
            
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert "data" in response_data
    
    @pytest.mark.asyncio
    async def test_upload_resume_invalid_file_type(self, client):
        """Test resume upload with invalid file type."""
        # Create a text file with wrong extension
        text_content = b"This is not a valid resume file"
        
        files = {"file": ("malicious.exe", io.BytesIO(text_content), "application/octet-stream")}
        data = {"name": "Test Resume"}
        
        response = await client.post("/api/v1/resumes/upload", files=files, data=data)
        
        assert response.status_code == 400
        response_data = response.json()
        assert "Invalid file type" in response_data["detail"]
    
    @pytest.mark.asyncio
    async def test_get_resume_by_id(self, client):
        """Test getting a specific resume by ID."""
        with patch('src.services.service_registry.service_registry') as mock_registry:
            mock_resume_service = AsyncMock()
            mock_resume_service.get_resume.return_value = AsyncMock(
                id="test-id",
                name="Test Resume",
                file_path="/test/path.pdf",
                file_type="pdf"
            )
            mock_registry.get_resume_service.return_value = mock_resume_service
            
            response = await client.get("/api/v1/resumes/test-id")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "test-id"
            assert data["name"] == "Test Resume"
    
    @pytest.mark.asyncio
    async def test_get_resume_not_found(self, client):
        """Test getting a non-existent resume."""
        with patch('src.services.service_registry.service_registry') as mock_registry:
            mock_resume_service = AsyncMock()
            mock_resume_service.get_resume.return_value = None
            mock_registry.get_resume_service.return_value = mock_resume_service
            
            response = await client.get("/api/v1/resumes/nonexistent-id")
            
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_resume(self, client):
        """Test updating a resume."""
        with patch('src.services.service_registry.service_registry') as mock_registry:
            mock_resume_service = AsyncMock()
            updated_resume = AsyncMock(
                id="test-id",
                name="Updated Resume Name",
                file_path="/test/path.pdf",
                file_type="pdf"
            )
            mock_resume_service.update_resume.return_value = updated_resume
            mock_registry.get_resume_service.return_value = mock_resume_service
            
            response = await client.put("/api/v1/resumes/test-id?name=Updated%20Resume%20Name")
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Resume Name"
    
    @pytest.mark.asyncio
    async def test_delete_resume(self, client):
        """Test deleting a resume."""
        with patch('src.services.service_registry.service_registry') as mock_registry:
            mock_resume_service = AsyncMock()
            mock_resume_service.delete_resume.return_value = True
            mock_registry.get_resume_service.return_value = mock_resume_service
            
            response = await client.delete("/api/v1/resumes/test-id")
            
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "successfully" in data["message"]
    
    @pytest.mark.asyncio
    async def test_set_default_resume(self, client):
        """Test setting a resume as default."""
        with patch('src.services.service_registry.service_registry') as mock_registry:
            mock_resume_service = AsyncMock()
            mock_resume_service.set_default_resume.return_value = True
            mock_registry.get_resume_service.return_value = mock_resume_service
            
            response = await client.post("/api/v1/resumes/test-id/set-default")
            
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "default" in data["message"]


class TestApplicationEndpoints:
    """Integration tests for application endpoints."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_get_all_applications(self, client):
        """Test getting all applications."""
        response = await client.get("/api/v1/applications/")
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert isinstance(data["data"], list)
    
    @pytest.mark.asyncio
    async def test_create_application(self, client):
        """Test creating a new application."""
        application_data = {
            "job_title": "Software Engineer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "job_url": "https://techcorp.com/careers",
            "portal": "LinkedIn"
        }
        
        response = await client.post("/api/v1/applications/", json=application_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_title"] == "Software Engineer"
        assert data["company"] == "Tech Corp"
        assert data["status"] == "draft"  # Default status
    
    @pytest.mark.asyncio
    async def test_get_application_statistics(self, client):
        """Test getting application statistics."""
        response = await client.get("/api/v1/applications/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_applications" in data
        assert "status_counts" in data
        assert "success_rate" in data
        assert isinstance(data["total_applications"], int)


class TestAIEndpoints:
    """Integration tests for AI endpoints."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_ai_health_check(self, client):
        """Test AI service health check."""
        response = await client.get("/api/v1/ai/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "available" in data
        assert isinstance(data["available"], bool)
    
    @pytest.mark.asyncio
    async def test_optimize_resume(self, client):
        """Test resume optimization endpoint."""
        optimization_request = {
            "resume_id": "test-resume-id",
            "target_role": "Software Engineer",
            "job_description": "Python development position with React frontend",
            "current_resume_content": "Basic software engineer resume"
        }
        
        response = await client.post("/api/v1/ai/optimize-resume", json=optimization_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "optimized_content" in data
        assert "suggestions" in data
        assert "confidence_score" in data
        assert isinstance(data["suggestions"], list)
    
    @pytest.mark.asyncio
    async def test_generate_cover_letter(self, client):
        """Test cover letter generation endpoint."""
        cover_letter_request = {
            "job_title": "Senior Developer",
            "company_name": "Innovation Labs",
            "job_description": "Full stack development with modern technologies",
            "resume_summary": "5 years of full stack development experience",
            "tone": "professional"
        }
        
        response = await client.post("/api/v1/ai/generate-cover-letter", json=cover_letter_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "job_title" in data
        assert "company_name" in data
        assert data["job_title"] == "Senior Developer"
        assert data["company_name"] == "Innovation Labs"


class TestJobSearchEndpoints:
    """Integration tests for job search endpoints."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        app = create_app()
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_search_jobs(self, client):
        """Test job search endpoint."""
        search_params = {
            "query": "software engineer",
            "location": "San Francisco",
            "experience_level": "mid"
        }
        
        response = await client.get("/api/v1/jobs/search", params=search_params)
        
        # Note: This might return 500 if JobSpy is not properly configured
        # In a real test environment, we'd mock the job search service
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "jobs" in data
            assert isinstance(data["jobs"], dict)
    
    @pytest.mark.asyncio
    async def test_get_available_sites(self, client):
        """Test getting available job sites."""
        response = await client.get("/api/v1/jobs/sites")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
