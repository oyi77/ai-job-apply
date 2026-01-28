"""Unit tests for AI Service API endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.dependencies import get_current_user
from src.models.user import UserProfile
from src.models.resume import (
    Resume,
    ResumeOptimizationResponse,
)
from src.models.cover_letter import CoverLetter
from src.models.career_insights import CareerInsightsResponse


@pytest.fixture
def mock_current_user():
    """Mock current user for dependency injection."""
    return UserProfile(
        id="test-user-123",
        email="test@example.com",
        name="Test User",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_resume():
    """Mock resume for testing."""
    return Resume(
        id="resume-123",
        name="Test Resume",
        file_path="/uploads/test-resume.pdf",
        file_type="pdf",
        content="Experienced Python developer with 5 years of experience...",
        user_id="test-user-123",
        is_default=True,
        skills=["Python", "FastAPI", "Docker"],
        experience_years=5,
        education=["BS Computer Science"],
        certifications=["AWS Certified"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_ai_service(mock_resume):
    """Mock AI service with all methods."""
    service = AsyncMock()

    # Mock resume optimization response
    optimization_response = ResumeOptimizationResponse(
        original_resume=mock_resume,
        optimized_content="Optimized resume content with improved keywords...",
        suggestions=["Add metrics", "Improve formatting"],
        skill_gaps=["Kubernetes", "Terraform"],
        improvements=["Added metrics", "Improved formatting"],
        confidence_score=0.85,
        ats_score=0.92,
        ats_checks={"keyword_match": 0.9, "formatting": 0.95},
        ats_recommendations=["Add more industry keywords"],
        timestamp=datetime.now(timezone.utc),
    )

    # Mock cover letter response
    cover_letter = CoverLetter(
        id="cl-123",
        job_title="Senior Python Developer",
        company_name="TechCorp",
        content="Dear Hiring Manager,\n\nI am excited to apply...",
        word_count=250,
        tone="professional",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        generated_at=datetime.now(timezone.utc),
    )

    # Mock career insights response
    career_insights = CareerInsightsResponse(
        market_analysis="Strong demand for Python developers in tech industry",
        salary_insights={"min": 120000, "max": 150000, "average": 135000},
        recommended_roles=["Senior Developer", "Tech Lead"],
        skill_gaps=["Leadership", "Public speaking"],
        strategic_advice=["Focus on cloud technologies", "Build leadership skills"],
        confidence_score=0.85,
    )

    # Setup mock methods
    service.optimize_resume = AsyncMock(return_value=optimization_response)
    service.generate_cover_letter = AsyncMock(return_value=cover_letter)
    service.analyze_job_match = AsyncMock(
        return_value={
            "match_score": 0.85,
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["Kubernetes"],
            "match_percentage": 85,
        }
    )
    service.extract_resume_skills = AsyncMock(
        return_value=["Python", "FastAPI", "SQL", "Docker", "AWS", "Leadership"]
    )
    service.suggest_resume_improvements = AsyncMock(
        return_value=[
            "Add quantifiable achievements",
            "Improve action verbs",
            "Add technical skills section",
            "Include relevant certifications",
            "Highlight leadership experience",
            "Add project outcomes",
        ]
    )
    service.generate_career_insights = AsyncMock(return_value=career_insights)
    service.prepare_interview = AsyncMock(
        return_value={
            "technical_questions": [
                "Tell us about your experience with Python",
                "How do you handle tight deadlines?",
            ],
            "behavioral_questions": [
                "Describe a challenging project",
                "How do you work in a team?",
            ],
            "tips": ["Research the company", "Practice your answers"],
            "company_research": {"culture": "TechCorp is a leading AI company"},
        }
    )
    service.is_available = AsyncMock(return_value=True)

    return service


@pytest.fixture
def app_with_auth(mock_current_user):
    """Create FastAPI app with mocked authentication."""
    app = create_app()

    # Override the get_current_user dependency
    async def override_get_current_user():
        return mock_current_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    return app


@pytest.fixture
def client_authenticated(app_with_auth):
    """Create authenticated test client."""
    return TestClient(app_with_auth)


@pytest.fixture
def client_unauthenticated():
    """Create unauthenticated test client."""
    app = create_app()
    return TestClient(app)


# =============================================================================
# Tests for /optimize-resume endpoint
# =============================================================================


class TestOptimizeResumeEndpoint:
    """Test cases for POST /api/v1/ai/optimize-resume endpoint."""

    @pytest.mark.asyncio
    async def test_optimize_resume_success(self, client_authenticated, mock_ai_service):
        """Test successful resume optimization."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/optimize-resume",
                json={
                    "resume_id": "resume-123",
                    "job_description": "We are looking for a Senior Python Developer...",
                    "target_role": "Senior Python Developer",
                    "company_name": "TechCorp Inc.",
                    "optimization_focus": ["skills", "experience"],
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "optimized_content" in data
            assert "suggestions" in data
            assert "confidence_score" in data
            assert data["confidence_score"] == 0.85

    @pytest.mark.asyncio
    async def test_optimize_resume_failure_returns_500(
        self, client_authenticated, mock_ai_service
    ):
        """Test resume optimization failure returns 500."""
        mock_ai_service.optimize_resume = AsyncMock(
            side_effect=Exception("AI service unavailable")
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/optimize-resume",
                json={
                    "resume_id": "resume-123",
                    "job_description": "Job description...",
                    "target_role": "Developer",
                },
            )

            assert response.status_code == 500
            assert "Resume optimization failed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_optimize_resume_unauthorized(self, client_unauthenticated):
        """Test resume optimization without authentication returns 401."""
        response = client_unauthenticated.post(
            "/api/v1/ai/optimize-resume",
            json={
                "resume_id": "resume-123",
                "job_description": "Job description...",
                "target_role": "Developer",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_optimize_resume_missing_required_fields(self, client_authenticated):
        """Test resume optimization with missing required fields returns 422."""
        response = client_authenticated.post(
            "/api/v1/ai/optimize-resume",
            json={
                "resume_id": "resume-123",
                # Missing job_description and target_role
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_optimize_resume_response_structure(
        self, client_authenticated, mock_ai_service
    ):
        """Test resume optimization response has correct structure."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/optimize-resume",
                json={
                    "resume_id": "resume-123",
                    "job_description": "We need a Python developer",
                    "target_role": "Senior Python Developer",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "optimized_content" in data
            assert "suggestions" in data
            assert "improvements" in data
            assert "confidence_score" in data
            assert isinstance(data["suggestions"], list)
            assert isinstance(data["confidence_score"], (int, float))


# =============================================================================
# Tests for /generate-cover-letter endpoint
# =============================================================================


class TestGenerateCoverLetterEndpoint:
    """Test cases for POST /api/v1/ai/generate-cover-letter endpoint."""

    @pytest.mark.asyncio
    async def test_generate_cover_letter_success(
        self, client_authenticated, mock_ai_service
    ):
        """Test successful cover letter generation."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/generate-cover-letter",
                json={
                    "job_title": "Senior Python Developer",
                    "company_name": "TechCorp Inc.",
                    "job_description": "We are looking for a Python developer...",
                    "resume_summary": "Experienced Python developer with 5 years...",
                    "tone": "professional",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "content" in data
            assert "job_title" in data
            assert data["job_title"] == "Senior Python Developer"
            assert data["company_name"] == "TechCorp"

    @pytest.mark.asyncio
    async def test_generate_cover_letter_failure_returns_500(
        self, client_authenticated, mock_ai_service
    ):
        """Test cover letter generation failure returns 500."""
        mock_ai_service.generate_cover_letter = AsyncMock(
            side_effect=Exception("AI service error")
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/generate-cover-letter",
                json={
                    "job_title": "Developer",
                    "company_name": "Company",
                    "job_description": "Description",
                    "resume_summary": "Summary",
                },
            )

            assert response.status_code == 500
            assert "Cover letter generation failed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_generate_cover_letter_unauthorized(self, client_unauthenticated):
        """Test cover letter generation without authentication returns 401."""
        response = client_unauthenticated.post(
            "/api/v1/ai/generate-cover-letter",
            json={
                "job_title": "Developer",
                "company_name": "Company",
                "job_description": "Description",
                "resume_summary": "Summary",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_generate_cover_letter_missing_required_fields(
        self, client_authenticated
    ):
        """Test cover letter generation with missing required fields returns 422."""
        response = client_authenticated.post(
            "/api/v1/ai/generate-cover-letter",
            json={
                "job_title": "Developer",
                # Missing company_name, job_description, resume_summary
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_generate_cover_letter_response_structure(
        self, client_authenticated, mock_ai_service
    ):
        """Test cover letter generation response has correct structure."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/generate-cover-letter",
                json={
                    "job_title": "Senior Python Developer",
                    "company_name": "TechCorp",
                    "job_description": "We need a Python developer",
                    "resume_summary": "Experienced Python developer",
                    "tone": "professional",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "content" in data
            assert "word_count" in data
            assert "tone" in data
            assert isinstance(data["word_count"], int)


# =============================================================================
# Tests for /analyze-job-match endpoint
# =============================================================================


class TestAnalyzeJobMatchEndpoint:
    """Test cases for POST /api/v1/ai/analyze-job-match endpoint."""

    @pytest.mark.asyncio
    async def test_analyze_job_match_success(
        self, client_authenticated, mock_ai_service
    ):
        """Test successful job match analysis."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/analyze-job-match",
                params={
                    "resume_content": "Experienced Python developer...",
                    "job_description": "Looking for a Python developer...",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "match_score" in data
            assert data["match_score"] == 0.85

    @pytest.mark.asyncio
    async def test_analyze_job_match_failure_returns_500(
        self, client_authenticated, mock_ai_service
    ):
        """Test job match analysis failure returns 500."""
        mock_ai_service.analyze_job_match = AsyncMock(
            side_effect=Exception("Analysis failed")
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/analyze-job-match",
                params={
                    "resume_content": "Resume content",
                    "job_description": "Job description",
                },
            )

            assert response.status_code == 500
            assert "Job match analysis failed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_analyze_job_match_unauthorized(self, client_unauthenticated):
        """Test job match analysis without authentication returns 401."""
        response = client_unauthenticated.post(
            "/api/v1/ai/analyze-job-match",
            params={
                "resume_content": "Resume content",
                "job_description": "Job description",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_analyze_job_match_high_score(
        self, client_authenticated, mock_ai_service
    ):
        """Test job match analysis with high match score."""
        mock_ai_service.analyze_job_match = AsyncMock(
            return_value={
                "match_score": 0.95,
                "matched_skills": ["Python", "FastAPI", "SQL"],
                "missing_skills": [],
                "match_percentage": 95,
            }
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/analyze-job-match",
                params={
                    "resume_content": "Expert Python developer",
                    "job_description": "Senior Python developer needed",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["match_score"] >= 0.9

    @pytest.mark.asyncio
    async def test_analyze_job_match_low_score(
        self, client_authenticated, mock_ai_service
    ):
        """Test job match analysis with low match score."""
        mock_ai_service.analyze_job_match = AsyncMock(
            return_value={
                "match_score": 0.35,
                "matched_skills": ["Communication"],
                "missing_skills": ["Python", "FastAPI", "SQL", "Docker"],
                "match_percentage": 35,
            }
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/analyze-job-match",
                params={
                    "resume_content": "Marketing manager background",
                    "job_description": "Senior Python developer needed",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["match_score"] < 0.5


# =============================================================================
# Tests for /extract-skills endpoint
# =============================================================================


class TestExtractSkillsEndpoint:
    """Test cases for POST /api/v1/ai/extract-skills endpoint."""

    @pytest.mark.asyncio
    async def test_extract_skills_success(self, client_authenticated, mock_ai_service):
        """Test successful skills extraction."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/extract-skills",
                params={"resume_content": "Experienced Python developer with AWS..."},
            )

            assert response.status_code == 200
            data = response.json()
            assert "all_skills" in data
            assert "confidence" in data
            assert "technical_skills" in data
            assert "soft_skills" in data
            assert "tools" in data

    @pytest.mark.asyncio
    async def test_extract_skills_failure_returns_500(
        self, client_authenticated, mock_ai_service
    ):
        """Test skills extraction failure returns 500."""
        mock_ai_service.extract_resume_skills = AsyncMock(
            side_effect=Exception("Extraction failed")
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/extract-skills",
                params={"resume_content": "Resume content"},
            )

            assert response.status_code == 500
            assert "Skills extraction failed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_extract_skills_unauthorized(self, client_unauthenticated):
        """Test skills extraction without authentication returns 401."""
        response = client_unauthenticated.post(
            "/api/v1/ai/extract-skills",
            params={"resume_content": "Resume content"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_extract_skills_response_structure(
        self, client_authenticated, mock_ai_service
    ):
        """Test skills extraction response has correct structure."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/extract-skills",
                params={"resume_content": "Python, FastAPI, SQL developer"},
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "all_skills" in data
            assert isinstance(data["all_skills"], list)
            assert "confidence" in data
            assert isinstance(data["confidence"], (int, float))


# =============================================================================
# Tests for /improve-resume endpoint
# =============================================================================


class TestImproveResumeEndpoint:
    """Test cases for POST /api/v1/ai/improve-resume endpoint."""

    @pytest.mark.asyncio
    async def test_improve_resume_success(self, client_authenticated, mock_ai_service):
        """Test successful resume improvement suggestions."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/improve-resume",
                params={"resume_content": "My resume content here..."},
            )

            assert response.status_code == 200
            data = response.json()
            assert "content_improvements" in data
            assert "format_improvements" in data
            assert "all_suggestions" in data
            assert "priority" in data
            assert "estimated_impact" in data

    @pytest.mark.asyncio
    async def test_improve_resume_failure_returns_500(
        self, client_authenticated, mock_ai_service
    ):
        """Test resume improvement failure returns 500."""
        mock_ai_service.suggest_resume_improvements = AsyncMock(
            side_effect=Exception("Improvement analysis failed")
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/improve-resume",
                params={"resume_content": "Resume content"},
            )

            assert response.status_code == 500
            assert "Failed to get improvement suggestions" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_improve_resume_unauthorized(self, client_unauthenticated):
        """Test resume improvement without authentication returns 401."""
        response = client_unauthenticated.post(
            "/api/v1/ai/improve-resume",
            params={"resume_content": "Resume content"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_improve_resume_response_structure(
        self, client_authenticated, mock_ai_service
    ):
        """Test resume improvement response has correct structure."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/improve-resume",
                params={"resume_content": "My resume content"},
            )

            assert response.status_code == 200
            data = response.json()
            assert "content_improvements" in data
            assert "format_improvements" in data
            assert "keyword_optimization" in data
            assert "all_suggestions" in data
            assert "priority" in data
            assert "estimated_impact" in data
            assert isinstance(data["all_suggestions"], list)


# =============================================================================
# Tests for /career-insights endpoint
# =============================================================================


class TestCareerInsightsEndpoint:
    """Test cases for POST /api/v1/ai/career-insights endpoint."""

    @pytest.mark.asyncio
    async def test_career_insights_success(self, client_authenticated, mock_ai_service):
        """Test successful career insights generation."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/career-insights",
                json={
                    "application_history": [
                        {"company": "TechCorp", "status": "rejected"},
                        {"company": "StartupXYZ", "status": "interview"},
                    ],
                    "skills": ["Python", "FastAPI", "Docker"],
                    "experience_level": "mid",
                    "career_goals": "Become a tech lead",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "market_analysis" in data
            assert "salary_insights" in data
            assert "recommended_roles" in data
            assert "skill_gaps" in data
            assert "strategic_advice" in data
            assert "confidence_score" in data

    @pytest.mark.asyncio
    async def test_career_insights_failure_returns_500(
        self, client_authenticated, mock_ai_service
    ):
        """Test career insights generation failure returns 500."""
        mock_ai_service.generate_career_insights = AsyncMock(
            side_effect=Exception("Insights generation failed")
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/career-insights",
                json={
                    "application_history": [],
                    "skills": ["Python"],
                },
            )

            assert response.status_code == 500
            assert "Career insights generation failed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_career_insights_unauthorized(self, client_unauthenticated):
        """Test career insights without authentication returns 401."""
        response = client_unauthenticated.post(
            "/api/v1/ai/career-insights",
            json={
                "application_history": [],
                "skills": ["Python"],
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_career_insights_response_structure(
        self, client_authenticated, mock_ai_service
    ):
        """Test career insights response has correct structure."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/career-insights",
                json={
                    "application_history": [{"company": "Test", "status": "applied"}],
                    "skills": ["Python", "FastAPI"],
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "market_analysis" in data
            assert "salary_insights" in data
            assert "recommended_roles" in data
            assert isinstance(data["recommended_roles"], list)
            assert "confidence_score" in data


# =============================================================================
# Tests for /interview-prep endpoint
# =============================================================================


class TestInterviewPrepEndpoint:
    """Test cases for POST /api/v1/ai/interview-prep endpoint."""

    @pytest.mark.asyncio
    async def test_interview_prep_success(self, client_authenticated, mock_ai_service):
        """Test successful interview preparation."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/interview-prep",
                json={
                    "job_description": "Senior Python Developer position...",
                    "resume_content": "Experienced Python developer...",
                    "company_name": "TechCorp Inc.",
                    "job_title": "Senior Python Developer",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "technical_questions" in data
            assert "behavioral_questions" in data
            assert "tips" in data

    @pytest.mark.asyncio
    async def test_interview_prep_failure_returns_500(
        self, client_authenticated, mock_ai_service
    ):
        """Test interview preparation failure returns 500."""
        mock_ai_service.prepare_interview = AsyncMock(
            side_effect=Exception("Interview prep failed")
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/interview-prep",
                json={
                    "job_description": "Job description",
                    "resume_content": "Resume content",
                },
            )

            assert response.status_code == 500
            assert "Interview preparation failed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_interview_prep_unauthorized(self, client_unauthenticated):
        """Test interview preparation without authentication returns 401."""
        response = client_unauthenticated.post(
            "/api/v1/ai/interview-prep",
            json={
                "job_description": "Job description",
                "resume_content": "Resume content",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_interview_prep_minimal_request(
        self, client_authenticated, mock_ai_service
    ):
        """Test interview prep with minimal required fields."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/interview-prep",
                json={
                    "job_description": "Job description",
                    "resume_content": "Resume content",
                },
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_interview_prep_response_structure(
        self, client_authenticated, mock_ai_service
    ):
        """Test interview preparation response has correct structure."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/interview-prep",
                json={
                    "job_description": "We need a Python developer",
                    "resume_content": "Python developer with 5 years experience",
                    "company_name": "TechCorp",
                    "job_title": "Senior Python Developer",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "technical_questions" in data or "questions" in data
            assert "tips" in data
            assert isinstance(data["tips"], list)


# =============================================================================
# Tests for /health endpoint
# =============================================================================


class TestHealthEndpoint:
    """Test cases for GET /api/v1/ai/health endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client without auth override for health endpoint."""
        app = create_app()
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, client, mock_ai_service):
        """Test health check when AI service is healthy."""
        mock_ai_service.is_available = AsyncMock(return_value=True)

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client.get("/api/v1/ai/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["available"] is True
            assert "features" in data
            assert "timestamp" in data
            assert "resume_optimization" in data["features"]

    @pytest.mark.asyncio
    async def test_health_check_unavailable(self, client, mock_ai_service):
        """Test health check when AI service is unavailable."""
        mock_ai_service.is_available = AsyncMock(return_value=False)

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client.get("/api/v1/ai/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["available"] is False
            assert "message" in data

    @pytest.mark.asyncio
    async def test_health_check_error(self, client, mock_ai_service):
        """Test health check when an error occurs."""
        mock_ai_service.is_available = AsyncMock(
            side_effect=Exception("Connection error")
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client.get("/api/v1/ai/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"
            assert data["available"] is False
            assert "error" in data
            assert "Connection error" in data["error"]

    @pytest.mark.asyncio
    async def test_health_check_no_auth_required(self, client, mock_ai_service):
        """Test that health check does not require authentication."""
        mock_ai_service.is_available = AsyncMock(return_value=True)

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client.get("/api/v1/ai/health")

            # Should not return 401
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_check_features_list(self, client, mock_ai_service):
        """Test that health check returns complete features list."""
        mock_ai_service.is_available = AsyncMock(return_value=True)

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client.get("/api/v1/ai/health")

            assert response.status_code == 200
            data = response.json()
            expected_features = [
                "resume_optimization",
                "cover_letter_generation",
                "job_match_analysis",
                "skills_extraction",
                "resume_improvement",
                "career_insights",
                "interview_preparation",
            ]
            for feature in expected_features:
                assert feature in data["features"]

    @pytest.mark.asyncio
    async def test_health_check_response_structure(self, client, mock_ai_service):
        """Test health check response has correct structure."""
        mock_ai_service.is_available = AsyncMock(return_value=True)

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client.get("/api/v1/ai/health")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "status" in data
            assert "service" in data
            assert "available" in data
            assert "timestamp" in data
            assert "features" in data
            assert isinstance(data["features"], list)
            assert len(data["features"]) > 0


# =============================================================================
# Tests for AI service fallback behavior
# =============================================================================


class TestAIServiceFallback:
    """Test cases for AI service fallback behavior."""

    @pytest.mark.asyncio
    async def test_ai_service_unavailable_optimize_resume(
        self, client_authenticated, mock_ai_service
    ):
        """Test resume optimization when AI service is unavailable."""
        mock_ai_service.is_available = AsyncMock(return_value=False)
        mock_ai_service.optimize_resume = AsyncMock(
            side_effect=Exception("AI service unavailable")
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/optimize-resume",
                json={
                    "resume_id": "resume-123",
                    "job_description": "We need a Python developer",
                    "target_role": "Senior Python Developer",
                },
            )

            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_ai_service_timeout(self, client_authenticated, mock_ai_service):
        """Test AI service timeout handling."""
        mock_ai_service.optimize_resume = AsyncMock(
            side_effect=TimeoutError("Request timeout")
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/optimize-resume",
                json={
                    "resume_id": "resume-123",
                    "job_description": "We need a Python developer",
                    "target_role": "Senior Python Developer",
                },
            )

            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_ai_service_connection_error(
        self, client_authenticated, mock_ai_service
    ):
        """Test AI service connection error handling."""
        mock_ai_service.generate_cover_letter = AsyncMock(
            side_effect=ConnectionError("Failed to connect to AI service")
        )

        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/generate-cover-letter",
                json={
                    "job_title": "Developer",
                    "company_name": "Company",
                    "job_description": "Description",
                    "resume_summary": "Summary",
                },
            )

            assert response.status_code == 500


# =============================================================================
# Additional edge case tests
# =============================================================================


class TestAIServiceEdgeCases:
    """Test edge cases and validation for AI service endpoints."""

    @pytest.mark.asyncio
    async def test_career_insights_empty_skills(
        self, client_authenticated, mock_ai_service
    ):
        """Test career insights with empty skills list."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/career-insights",
                json={
                    "application_history": [],
                    "skills": [],  # Empty skills
                },
            )
            # Should still work with empty skills
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_interview_prep_with_all_optional_fields(
        self, client_authenticated, mock_ai_service
    ):
        """Test interview prep with all optional fields provided."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/interview-prep",
                json={
                    "job_description": "Description",
                    "resume_content": "Content",
                    "company_name": "TechCorp",
                    "job_title": "Developer",
                },
            )
            assert response.status_code == 200
            # Verify the service was called with all parameters
            mock_ai_service.prepare_interview.assert_called_once()

    @pytest.mark.asyncio
    async def test_cover_letter_with_custom_tone(
        self, client_authenticated, mock_ai_service
    ):
        """Test cover letter generation with custom tone."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/generate-cover-letter",
                json={
                    "job_title": "Developer",
                    "company_name": "Company",
                    "job_description": "Description",
                    "resume_summary": "Summary",
                    "tone": "confident",
                },
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_optimize_resume_with_optimization_focus(
        self, client_authenticated, mock_ai_service
    ):
        """Test resume optimization with specific focus areas."""
        with patch(
            "src.services.service_registry.service_registry.get_ai_service",
            new_callable=AsyncMock,
            return_value=mock_ai_service,
        ):
            response = client_authenticated.post(
                "/api/v1/ai/optimize-resume",
                json={
                    "resume_id": "resume-123",
                    "job_description": "Description",
                    "target_role": "Developer",
                    "optimization_focus": ["skills", "experience", "achievements"],
                },
            )
            assert response.status_code == 200
