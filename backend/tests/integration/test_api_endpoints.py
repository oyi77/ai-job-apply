"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
import tempfile
import io
from pathlib import Path

from src.api.app import create_app


@pytest.fixture
def mock_service_registry():
    """Create a mock service registry with all required services."""
    mock_registry = MagicMock()
    
    # Mock file service
    mock_file_service = AsyncMock()
    mock_file_service.save_file.return_value = True
    mock_file_service.read_file.return_value = b"test content"
    
    # Mock resume service
    mock_resume_service = AsyncMock()
    mock_resume_service.get_all_resumes.return_value = []
    mock_resume_service.get_resume.return_value = None
    
    # Mock application service
    mock_app_service = AsyncMock()
    mock_app_service.get_all_applications.return_value = []
    mock_app_service.get_application_stats.return_value = {
        "total_applications": 0,
        "status_counts": {},
        "success_rate": 0.0
    }
    
    # Mock AI service
    mock_ai_service = AsyncMock()
    mock_ai_service.is_available.return_value = True
    mock_ai_service.optimize_resume.return_value = MagicMock(
        optimized_content="optimized",
        suggestions=["suggestion1"],
        confidence_score=0.85
    )
    mock_ai_service.generate_cover_letter.return_value = MagicMock(
        content="cover letter content",
        job_title="Test Job",
        company_name="Test Company"
    )
    
    # Mock cover letter service
    mock_cover_letter_service = AsyncMock()
    
    # Mock job search service
    mock_job_search_service = AsyncMock()
    mock_job_search_service.search_jobs.return_value = {"jobs": {}}
    mock_job_search_service.get_available_sites.return_value = ["linkedin", "indeed"]
    
    # Mock job application service
    mock_job_app_service = AsyncMock()
    
    # Configure registry methods
    mock_registry.initialize = AsyncMock()
    mock_registry.health_check = AsyncMock(return_value={
        "service_registry": "healthy",
        "services": {}
    })
    
    # Store services on the registry for easy access in tests
    mock_registry.file_service = mock_file_service
    mock_registry.resume_service = mock_resume_service
    mock_registry.app_service = mock_app_service
    mock_registry.ai_service = mock_ai_service
    mock_registry.cover_letter_service = mock_cover_letter_service
    mock_registry.job_search_service = mock_job_search_service
    mock_registry.job_app_service = mock_job_app_service
    
    mock_registry.get_file_service.side_effect = lambda: mock_registry.file_service
    mock_registry.get_resume_service.side_effect = lambda: mock_registry.resume_service
    mock_registry.get_application_service.side_effect = lambda: mock_registry.app_service
    mock_registry.get_ai_service.side_effect = lambda: mock_registry.ai_service
    mock_registry.get_cover_letter_service.side_effect = lambda: mock_registry.cover_letter_service
    mock_registry.get_job_search_service.side_effect = lambda: mock_registry.job_search_service
    mock_registry.get_job_application_service.side_effect = lambda: mock_registry.job_app_service
    
    return mock_registry


@pytest.fixture
async def client(mock_service_registry):
    """Create test client with mocked service registry."""
    from src.services.service_registry import service_registry
    
    # Patch the methods on the actual global service_registry instance
    # We patch multiple modules to be safe, as some might have different imports
    patches = [
        patch.object(service_registry, 'get_file_service', AsyncMock(return_value=mock_service_registry.file_service)),
        patch.object(service_registry, 'get_resume_service', AsyncMock(return_value=mock_service_registry.resume_service)),
        patch.object(service_registry, 'get_application_service', AsyncMock(return_value=mock_service_registry.app_service)),
        patch.object(service_registry, 'get_ai_service', AsyncMock(return_value=mock_service_registry.ai_service)),
        patch.object(service_registry, 'get_cover_letter_service', AsyncMock(return_value=mock_service_registry.cover_letter_service)),
        patch.object(service_registry, 'get_job_search_service', AsyncMock(return_value=mock_service_registry.job_search_service)),
        patch.object(service_registry, 'get_job_application_service', AsyncMock(return_value=mock_service_registry.job_app_service))
    ]
    
    # Apply all patches
    for p in patches:
        p.start()
        
    try:
        app = create_app()
        
        # Mock current user to bypass authentication
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        
        from src.api.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: mock_user
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        # Stop all patches
        for p in reversed(patches):
            p.stop()
        
        # Clean up overrides
        if 'app' in locals():
            app.dependency_overrides = {}


class TestResumeEndpoints:
    """Integration tests for resume endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_all_resumes(self, client, mock_service_registry):
        """Test getting all resumes."""
        from src.models.resume import Resume
        # Configure real models
        mock_resumes = [
            Resume(id="1", name="Resume 1", file_path="/path/1.pdf", file_type="pdf"),
            Resume(id="2", name="Resume 2", file_path="/path/2.pdf", file_type="pdf")
        ]
        mock_service_registry.resume_service.get_all_resumes.return_value = mock_resumes
        
        response = await client.get("/api/v1/resumes")
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 2
    
    @pytest.mark.asyncio
    async def test_upload_resume_success(self, client, mock_service_registry):
        """Test successful resume upload."""
        from src.models.resume import Resume
        # Create a temporary PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        
        # Configure existing services from registry
        mock_file_service = mock_service_registry.file_service
        mock_file_service.save_file = AsyncMock(return_value=True)
        mock_service_registry.file_service = mock_file_service
        
        mock_resume = Resume(
            id="test-id",
            name="test_resume.pdf",
            file_path="/test/path.pdf",
            file_type="pdf",
            is_default=True
        )
        mock_service_registry.resume_service.upload_resume.return_value = mock_resume
        
        # Upload file
        files = {"file": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")}
        data = {"name": "Test Resume"}
        
        response = await client.post("/api/v1/resumes/upload", files=files, data=data)
        
        if response.status_code != 200:
            print(f"FAILED: {response.status_code} - {response.text}")
            
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
    async def test_get_resume_by_id(self, client, mock_service_registry):
        """Test getting a specific resume by ID."""
        from src.models.resume import Resume
        # Create a real Resume object
        mock_resume = Resume(
            id="test-id",
            name="Test Resume",
            file_path="/test/path.pdf",
            file_type="pdf"
        )
        
        mock_service_registry.resume_service.get_resume.return_value = mock_resume
        
        response = await client.get("/api/v1/resumes/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-id"
        assert data["name"] == "Test Resume"
    
    @pytest.mark.asyncio
    async def test_get_resume_not_found(self, client, mock_service_registry):
        """Test getting a non-existent resume."""
        mock_service_registry.resume_service.get_resume.return_value = None
        
        response = await client.get("/api/v1/resumes/nonexistent-id")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_resume(self, client, mock_service_registry):
        """Test updating a resume."""
        from src.models.resume import Resume
        updated_resume = Resume(
            id="test-id",
            name="Updated Resume Name",
            file_path="/test/path.pdf",
            file_type="pdf"
        )
        
        mock_service_registry.resume_service.update_resume.return_value = updated_resume
        
        response = await client.put("/api/v1/resumes/test-id?name=Updated%20Resume%20Name")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Resume Name"
    
    @pytest.mark.asyncio
    async def test_delete_resume(self, client, mock_service_registry):
        """Test deleting a resume."""
        mock_service_registry.resume_service.delete_resume.return_value = True
        
        response = await client.delete("/api/v1/resumes/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "successfully" in data["message"]
    
    @pytest.mark.asyncio
    async def test_set_default_resume(self, client, mock_service_registry):
        """Test setting a resume as default."""
        mock_service_registry.resume_service.set_default_resume.return_value = True
        
        response = await client.post("/api/v1/resumes/test-id/set-default")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "default" in data["message"]


class TestApplicationEndpoints:
    """Integration tests for application endpoints."""
    

    
    @pytest.mark.asyncio
    async def test_get_all_applications(self, client):
        """Test getting all applications."""
        response = await client.get("/api/v1/applications")
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert isinstance(data["data"], list)
    
    @pytest.mark.asyncio
    async def test_create_application(self, client, mock_service_registry):
        """Test creating a new application."""
        from src.models.application import JobApplication
        application_data = {
            "job_id": "test-job-id",
            "job_title": "Software Engineer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "job_url": "https://techcorp.com/careers",
            "portal": "LinkedIn"
        }
        
        # Mock create_application to return a real JobApplication
        mock_app = JobApplication(
            id="test-app-id",
            job_id="test-job-id",
            job_title="Software Engineer",
            company="Tech Corp",
            status="draft"
        )
        mock_service_registry.app_service.create_application.return_value = mock_app
        
        response = await client.post("/api/v1/applications/", json=application_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["job_title"] == "Software Engineer"
        assert data["data"]["company"] == "Tech Corp"
        assert data["data"]["status"] == "draft"  # Default status
    
    @pytest.mark.asyncio
    async def test_get_application_statistics(self, client, mock_service_registry):
        """Test getting application statistics."""
        # Configure already existing app_service from registry
        mock_service_registry.app_service.get_application_stats.return_value = {
            "total_applications": 10,
            "status_breakdown": {"draft": 5},
            "success_rate": 50.0
        }
        
        response = await client.get("/api/v1/applications/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_applications" in data["data"]
        assert "status_breakdown" in data["data"]
        assert "success_rate" in data["data"]
        assert data["data"]["total_applications"] == 10


class TestAIEndpoints:
    """Integration tests for AI endpoints."""
    

    
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
    async def test_optimize_resume(self, client, mock_service_registry):
        """Test resume optimization endpoint."""
        from src.models.resume import Resume, ResumeOptimizationResponse
        optimization_request = {
            "resume_id": "test-resume-id",
            "target_role": "Software Engineer",
            "job_description": "Python development position with React frontend",
            "current_resume_content": "Basic software engineer resume"
        }
        
        mock_resume = Resume(
            id="test-resume-id",
            name="Test Resume",
            file_path="/test/path.pdf",
            file_type="pdf"
        )
        
        mock_response = ResumeOptimizationResponse(
            original_resume=mock_resume,
            optimized_content="Optimized Content",
            suggestions=["Suggestion 1"],
            confidence_score=0.95,
            skill_gaps=[],
            improvements=[]
        )
        mock_service_registry.ai_service.optimize_resume.return_value = mock_response
        
        response = await client.post("/api/v1/ai/optimize-resume", json=optimization_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "optimized_content" in data
        assert "suggestions" in data
        assert "confidence_score" in data
        assert isinstance(data["suggestions"], list)
    
    @pytest.mark.asyncio
    async def test_generate_cover_letter(self, client, mock_service_registry):
        """Test cover letter generation endpoint."""
        from src.models.cover_letter import CoverLetter
        cover_letter_request = {
            "job_title": "Senior Developer",
            "company_name": "Innovation Labs",
            "job_description": "Full stack development with modern technologies",
            "resume_summary": "5 years of full stack development experience",
            "tone": "professional"
        }
        
        mock_cl = CoverLetter(
            id="test-cl-id",
            job_title="Senior Developer",
            company_name="Innovation Labs",
            content="Test content",
            job_description="Test description",
            tone="professional",
            word_count=200
        )
        mock_service_registry.ai_service.generate_cover_letter.return_value = mock_cl
        
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
    

    
    @pytest.mark.asyncio
    async def test_search_jobs(self, client, mock_service_registry):
        """Test job search endpoint."""
        from src.models.job import JobSearchResponse, Job
        # Configure already existing job_search_service from registry
        mock_jobs = {
            "linkedin": [
                Job(
                    title="Engineer", 
                    company="Corp",
                    location="SF",
                    url="http://example.com/",
                    portal="LinkedIn"
                )
            ]
        }
        mock_response = JobSearchResponse(
            jobs=mock_jobs,
            total_jobs=1,
            search_metadata={"keywords": ["software engineer"]}
        )
        mock_service_registry.job_search_service.search_jobs.return_value = mock_response
        
        search_request = {
            "keywords": ["software engineer"],
            "location": "San Francisco",
            "experience_level": "mid"
        }
        
        response = await client.post("/api/v1/jobs/search", json=search_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert isinstance(data["jobs"], dict)
        assert data["total_jobs"] == 1
    
    @pytest.mark.asyncio
    async def test_get_available_sites(self, client, mock_service_registry):
        """Test getting available job sites."""
        # This is a synchronous method in the service
        mock_service_registry.job_search_service.get_available_sites = MagicMock(return_value=["linkedin", "indeed"])
        
        response = await client.get("/api/v1/jobs/sites")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "linkedin" in data
