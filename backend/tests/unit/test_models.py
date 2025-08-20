"""Unit tests for data models."""

import pytest
from datetime import datetime
from src.models.job import Job, JobSearchRequest, JobSearchResponse, ExperienceLevel
from src.models.resume import Resume, ResumeOptimizationRequest
from src.models.application import JobApplication, ApplicationStatus
from src.models.cover_letter import CoverLetter, CoverLetterRequest


class TestJobModels:
    """Test job-related models."""
    
    def test_job_creation(self):
        """Test Job model creation."""
        job = Job(
            title="Python Developer",
            company="TechCorp",
            location="Remote",
            url="https://example.com/job",
            portal="indeed"
        )
        
        assert job.title == "Python Developer"
        assert job.company == "TechCorp"
        assert job.location == "Remote"
        assert job.portal == "indeed"
        assert job.created_at is not None
        assert job.updated_at is not None
    
    def test_job_search_request(self):
        """Test JobSearchRequest model."""
        request = JobSearchRequest(
            keywords=["python", "developer"],
            location="Remote",
            experience_level=ExperienceLevel.MID
        )
        
        assert request.keywords == ["python", "developer"]
        assert request.location == "Remote"
        assert request.experience_level == ExperienceLevel.MID
        assert request.results_wanted == 50  # default value
    
    def test_job_search_response(self):
        """Test JobSearchResponse model."""
        jobs = {"indeed": [Job(title="Test", company="Test", location="Test", url="https://test.com", portal="indeed")]}
        response = JobSearchResponse(
            jobs=jobs,
            total_jobs=1
        )
        
        assert response.total_jobs == 1
        assert "indeed" in response.jobs
        assert len(response.jobs["indeed"]) == 1


class TestResumeModels:
    """Test resume-related models."""
    
    def test_resume_creation(self):
        """Test Resume model creation."""
        resume = Resume(
            name="My Resume",
            file_path="./resumes/resume.pdf",
            file_type="pdf"
        )
        
        assert resume.name == "My Resume"
        assert resume.file_path == "./resumes/resume.pdf"
        assert resume.file_type == "pdf"
    
    def test_resume_optimization_request(self):
        """Test ResumeOptimizationRequest model."""
        request = ResumeOptimizationRequest(
            resume_id="res_123",
            job_description="We need a Python developer...",
            target_role="Python Developer",
            company_name="TechCorp"
        )
        
        assert request.resume_id == "res_123"
        assert request.target_role == "Python Developer"
        assert request.company_name == "TechCorp"


class TestApplicationModels:
    """Test application-related models."""
    
    def test_job_application_creation(self):
        """Test JobApplication model creation."""
        app = JobApplication(
            job_id="job_123",
            job_title="Python Developer",
            company="TechCorp"
        )
        
        assert app.job_id == "job_123"
        assert app.job_title == "Python Developer"
        assert app.company == "TechCorp"
        assert app.status == ApplicationStatus.DRAFT  # default value
    
    def test_application_status_enum(self):
        """Test ApplicationStatus enum values."""
        assert ApplicationStatus.DRAFT == "draft"
        assert ApplicationStatus.SUBMITTED == "submitted"
        assert ApplicationStatus.REJECTED == "rejected"


class TestCoverLetterModels:
    """Test cover letter-related models."""
    
    def test_cover_letter_request(self):
        """Test CoverLetterRequest model."""
        request = CoverLetterRequest(
            job_title="Python Developer",
            company_name="TechCorp",
            job_description="We need a developer...",
            resume_summary="Experienced Python developer..."
        )
        
        assert request.job_title == "Python Developer"
        assert request.company_name == "TechCorp"
        assert request.tone == "professional"  # default value
    
    def test_cover_letter_creation(self):
        """Test CoverLetter model creation."""
        cover_letter = CoverLetter(
            job_title="Python Developer",
            company_name="TechCorp",
            content="Dear Hiring Manager...",
            tone="professional",
            word_count=150
        )
        
        assert cover_letter.job_title == "Python Developer"
        assert cover_letter.word_count == 150
        assert cover_letter.reading_time_minutes == 0.8  # 150/200 = 0.75, rounded to 0.8
