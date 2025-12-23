"""Unit tests for AI service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys

# Mock dependencies before importing services
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['PyPDF2'] = MagicMock()
sys.modules['docx'] = MagicMock()

from src.services.gemini_ai_service import GeminiAIService
from src.models.resume import ResumeOptimizationRequest, ResumeOptimizationResponse
from src.models.cover_letter import CoverLetterRequest, CoverLetter


class TestGeminiAIService:
    """Test cases for GeminiAIService."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        config = MagicMock()
        config.GEMINI_API_KEY = "test_api_key"
        config.GEMINI_MODEL = "gemini-1.5-flash"
        return config
    
    @pytest.fixture
    def ai_service(self, mock_config):
        """Create AI service with mocked dependencies."""
        with patch('src.services.gemini_ai_service.config', mock_config):
            return GeminiAIService()
    
    @pytest.mark.asyncio
    async def test_is_available_with_api_key(self, ai_service):
        """Test service availability with API key."""
        with patch('src.services.gemini_ai_service.config.GEMINI_API_KEY', "test_key"):
            available = await ai_service.is_available()
            assert available is True
    
    @pytest.mark.asyncio
    async def test_is_available_without_api_key(self, ai_service):
        """Test service availability without API key."""
        with patch('src.services.gemini_ai_service.config.GEMINI_API_KEY', None):
            available = await ai_service.is_available()
            assert available is False
    
    @pytest.mark.asyncio
    async def test_optimize_resume_with_api_key(self, ai_service):
        """Test resume optimization with API key available."""
        # Mock the Gemini API response
        mock_response = MagicMock()
        mock_response.text = "Optimized resume content with improved keywords and structure."
        
        with patch('src.services.gemini_ai_service.genai.GenerativeModel') as mock_model_class:
            mock_model = MagicMock()
            mock_model.generate_content_async.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            request = ResumeOptimizationRequest(
                resume_id="test-resume-id",
                target_role="Software Engineer",
                job_description="Python developer position",
                current_resume_content="Basic resume content"
            )
            
            result = await ai_service.optimize_resume(request)
            
            # Assertions
            assert isinstance(result, ResumeOptimizationResponse)
            assert result.optimized_content == "Optimized resume content with improved keywords and structure."
            assert len(result.suggestions) > 0
            assert result.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_optimize_resume_fallback_without_api_key(self, ai_service):
        """Test resume optimization fallback without API key."""
        with patch('src.services.gemini_ai_service.config.GEMINI_API_KEY', None):
            request = ResumeOptimizationRequest(
                resume_id="test-resume-id",
                target_role="Software Engineer",
                job_description="Python developer position",
                current_resume_content="Basic resume content"
            )
            
            result = await ai_service.optimize_resume(request)
            
            # Should return mock response
            assert isinstance(result, ResumeOptimizationResponse)
            assert "Optimized resume for Software Engineer position" in result.optimized_content
            assert len(result.suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_generate_cover_letter_with_api_key(self, ai_service):
        """Test cover letter generation with API key available."""
        # Mock the Gemini API response
        mock_response = MagicMock()
        mock_response.text = "Professional cover letter content tailored to the position."
        
        with patch('src.services.gemini_ai_service.genai.GenerativeModel') as mock_model_class:
            mock_model = MagicMock()
            mock_model.generate_content_async.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            request = CoverLetterRequest(
                job_title="Software Engineer",
                company_name="Tech Corp",
                job_description="Python development position",
                resume_summary="5 years of Python experience",
                tone="professional"
            )
            
            result = await ai_service.generate_cover_letter(request)
            
            # Assertions
            assert isinstance(result, CoverLetter)
            assert result.job_title == "Software Engineer"
            assert result.company_name == "Tech Corp"
            assert result.content == "Professional cover letter content tailored to the position."
            assert result.tone == "professional"
    
    @pytest.mark.asyncio
    async def test_generate_cover_letter_fallback_without_api_key(self, ai_service):
        """Test cover letter generation fallback without API key."""
        with patch('src.services.gemini_ai_service.config.GEMINI_API_KEY', None):
            request = CoverLetterRequest(
                job_title="Software Engineer",
                company_name="Tech Corp",
                job_description="Python development position",
                resume_summary="5 years of Python experience",
                tone="professional"
            )
            
            result = await ai_service.generate_cover_letter(request)
            
            # Should return mock response
            assert isinstance(result, CoverLetter)
            assert result.job_title == "Software Engineer"
            assert result.company_name == "Tech Corp"
            assert "Tech Corp" in result.content
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, ai_service):
        """Test handling of API errors."""
        with patch('src.services.gemini_ai_service.genai.GenerativeModel') as mock_model_class:
            mock_model = MagicMock()
            mock_model.generate_content_async.side_effect = Exception("API Error")
            mock_model_class.return_value = mock_model
            
            request = ResumeOptimizationRequest(
                resume_id="test-resume-id",
                target_role="Software Engineer",
                job_description="Python developer position",
                current_resume_content="Basic resume content"
            )
            
            # Should fallback to mock response instead of raising exception
            result = await ai_service.optimize_resume(request)
            assert isinstance(result, ResumeOptimizationResponse)
    
    def test_extract_suggestions_from_text(self, ai_service):
        """Test suggestion extraction from AI response text."""
        text = """
        Here are some suggestions:
        1. Add more technical skills
        2. Include quantifiable achievements
        3. Improve formatting
        4. Add relevant certifications
        5. Tailor to job requirements
        6. Extra suggestion that should be filtered
        """
        
        suggestions = ai_service._extract_suggestions_from_text(text)
        
        assert len(suggestions) <= 5  # Should be limited to 5
        assert "Add more technical skills" in suggestions
        assert "Include quantifiable achievements" in suggestions
    
    def test_build_resume_optimization_prompt(self, ai_service):
        """Test resume optimization prompt building."""
        request = ResumeOptimizationRequest(
            resume_id="test-id",
            target_role="Data Scientist",
            job_description="Machine learning position requiring Python and SQL",
            current_resume_content="Software engineer with Python experience"
        )
        
        prompt = ai_service._build_resume_optimization_prompt(request)
        
        assert "Data Scientist" in prompt
        assert "Python" in prompt
        assert "optimize" in prompt.lower()
        assert "suggestions" in prompt.lower()
    
    def test_build_cover_letter_prompt(self, ai_service):
        """Test cover letter prompt building."""
        request = CoverLetterRequest(
            job_title="Frontend Developer",
            company_name="Design Studio",
            job_description="React and TypeScript development",
            resume_summary="3 years of React development",
            tone="friendly"
        )
        
        prompt = ai_service._build_cover_letter_prompt(request)
        
        assert "Frontend Developer" in prompt
        assert "Design Studio" in prompt
        assert "React" in prompt
        assert "friendly" in prompt.lower() or "casual" in prompt.lower()
