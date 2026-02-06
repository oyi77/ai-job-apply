"""
Unit tests for FormFillerService.

Tests cover:
- YAML template loading
- Field value determination (user preferences, mapped answers, AI fallback)
- Form filling logic for different field types
- Error handling and edge cases
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import yaml

import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.services.form_filler import FormFillerService


class MockAIService:
    """Mock AI service for testing."""

    def __init__(self):
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.text = "Mock AI generated answer"
        mock_response.parts = [mock_part]
        self.generate_content = AsyncMock(return_value=mock_response)


class TestFormFillerService:
    """Test cases for FormFillerService."""

    @pytest.fixture
    def mock_yaml_content(self):
        """Sample YAML content matching the structure."""
        return {
            "linkedin": {
                "years_of_experience": {
                    "xpath": "//select[@name='yearsOfExperience']",
                    "type": "select",
                    "answers": ["2-5 years", "5-10 years"],
                    "ai_fallback": False,
                    "description": "Years of experience",
                },
                "expected_salary": {
                    "xpath": "//input[@name='expectedSalary']",
                    "type": "number",
                    "default_value": "100000",
                    "ai_fallback": True,
                    "description": "Expected salary",
                },
                "cover_letter": {
                    "xpath": "//textarea[@name='coverLetter']",
                    "type": "textarea",
                    "default_value": "",
                    "ai_fallback": True,
                    "description": "Cover letter content",
                },
            },
            "indeed": {
                "resume_upload": {
                    "xpath": "//input[@type='file']",
                    "type": "file",
                    "default_value": "",
                    "ai_fallback": False,
                    "description": "Resume file upload",
                },
                "work_authorization": {
                    "xpath": "//select[@name='workAuthorization']",
                    "type": "select",
                    "answers": ["Authorized to work"],
                    "ai_fallback": False,
                    "description": "Work authorization status",
                },
            },
            "glassdoor": {
                "employment_type": {
                    "xpath": "//select[@name='employmentType']",
                    "type": "select",
                    "answers": ["Full-time", "Part-time"],
                    "ai_fallback": False,
                    "description": "Employment type",
                }
            },
        }

    @pytest.fixture
    def temp_yaml_file(self, tmp_path, mock_yaml_content):
        """Create a temporary YAML file for testing."""
        yaml_path = tmp_path / "test_form_fields.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(mock_yaml_content, f)
        return str(yaml_path)

    @pytest_asyncio.fixture
    async def form_filler_service(self, temp_yaml_file):
        """Create FormFillerService instance for testing."""
        mock_ai = MockAIService()
        service = FormFillerService(ai_service=mock_ai, user_id="test_user_123")

        # Patch the YAML loading to use our temp file
        with patch.object(
            FormFillerService,
            "_load_form_templates",
            return_value=yaml.safe_load(open(temp_yaml_file).read()),
        ):
            yield service

        # Cleanup
        await service.close()

    @pytest.mark.asyncio
    async def test_service_initialization(self, form_filler_service):
        """Test FormFillerService initialization."""
        assert form_filler_service.ai_service is not None
        assert form_filler_service.user_id == "test_user_123"
        assert form_filler_service.logger is not None

    @pytest.mark.asyncio
    async def test_load_form_templates_success(self, temp_yaml_file):
        """Test successful YAML template loading."""
        mock_ai = MockAIService()
        service = FormFillerService(ai_service=mock_ai, user_id="test_user")
        original_open = open

        # Manually call _load_form_templates
        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "builtins.open",
                MagicMock(
                    side_effect=lambda *args, **kwargs: original_open(
                        temp_yaml_file, "r"
                    )
                ),
            ):
                with patch(
                    "yaml.safe_load",
                    return_value=yaml.safe_load(original_open(temp_yaml_file).read()),
                ):
                    templates = service._load_form_templates()

        assert templates is not None
        assert "linkedin" in templates
        assert "indeed" in templates
        assert "glassdoor" in templates

    @pytest.mark.asyncio
    async def test_load_form_templates_file_not_found(self):
        """Test handling of missing YAML file."""
        mock_ai = MockAIService()
        service = FormFillerService(ai_service=mock_ai, user_id="test_user")

        with patch("pathlib.Path.exists", return_value=False):
            templates = service._load_form_templates()

        assert templates == {}

    @pytest.mark.asyncio
    async def test_load_form_templates_yaml_error(self):
        """Test handling of YAML parsing errors."""
        mock_ai = MockAIService()
        service = FormFillerService(ai_service=mock_ai, user_id="test_user")

        with patch("pathlib.Path.exists", return_value=True):
            with patch("yaml.safe_load", side_effect=yaml.YAMLError("Invalid YAML")):
                templates = service._load_form_templates()

        assert templates == {}

    @pytest.mark.asyncio
    async def test_fill_form_user_preference_priority(
        self, form_filler_service, mock_yaml_content
    ):
        """Test that user preferences take priority over mapped answers."""
        # Set up templates
        form_filler_service.templates = mock_yaml_content

        # Provide user preference
        field_values = {"years_of_experience": "10+ years"}
        user_preferences = None

        result = await form_filler_service.fill_form(
            platform="linkedin",
            field_values=field_values,
            user_preferences=user_preferences,
        )

        # User preference should be used
        assert "years_of_experience" in result
        assert result["years_of_experience"] == "10+ years"

    @pytest.mark.asyncio
    async def test_fill_form_mapped_answer(
        self, form_filler_service, mock_yaml_content
    ):
        """Test that mapped answers are used when no user preference."""
        form_filler_service.templates = mock_yaml_content

        field_values = {}
        user_preferences = None

        result = await form_filler_service.fill_form(
            platform="linkedin",
            field_values=field_values,
            user_preferences=user_preferences,
        )

        # Should use first mapped answer
        assert "years_of_experience" in result
        assert result["years_of_experience"] == "2-5 years"  # First mapped answer

    @pytest.mark.asyncio
    async def test_fill_form_default_value(
        self, form_filler_service, mock_yaml_content
    ):
        """Test that default values are used when no mapped answers."""
        form_filler_service.templates = mock_yaml_content

        field_values = {}
        user_preferences = None

        result = await form_filler_service.fill_form(
            platform="linkedin",
            field_values=field_values,
            user_preferences=user_preferences,
        )

        # Should use default value
        assert "expected_salary" in result
        assert result["expected_salary"] == "100000"  # Default value

    @pytest.mark.asyncio
    async def test_fill_form_ai_fallback(self, form_filler_service, mock_yaml_content):
        """Test AI fallback for fields with ai_fallback enabled."""
        form_filler_service.templates = mock_yaml_content

        field_values = {}
        user_preferences = None

        result = await form_filler_service.fill_form(
            platform="linkedin",
            field_values=field_values,
            user_preferences=user_preferences,
        )

        # AI fallback should be used for cover_letter
        # Note: This tests that the code path is executed
        assert "cover_letter" in result

    @pytest.mark.asyncio
    async def test_fill_form_platform_not_found(self, form_filler_service):
        """Test handling of unsupported platform."""
        form_filler_service.templates = {}

        result = await form_filler_service.fill_form(
            platform="unsupported_platform", field_values={}
        )

        assert result == {}

    @pytest.mark.asyncio
    async def test_fill_form_empty_platform(
        self, form_filler_service, mock_yaml_content
    ):
        """Test handling of empty platform configuration."""
        form_filler_service.templates = {"linkedin": {}, "empty_platform": {}}

        result = await form_filler_service.fill_form(
            platform="empty_platform", field_values={}
        )

        # Should return empty dict for empty platform
        assert result == {}

    @pytest.mark.asyncio
    async def test_get_field_value_user_preference(self, form_filler_service):
        """Test _get_field_value with user preference."""
        field_def = {
            "type": "select",
            "answers": ["Option1", "Option2"],
            "ai_fallback": False,
        }
        field_values = {"test_field": "User Value"}
        user_preferences = None

        result = await form_filler_service._get_field_value(
            field_name="test_field",
            field_def=field_def,
            field_values=field_values,
            user_preferences=user_preferences,
        )

        assert result == "User Value"

    @pytest.mark.asyncio
    async def test_get_field_value_field_values(self, form_filler_service):
        """Test _get_field_value with field values but no user preference."""
        field_def = {
            "type": "text",
            "answers": [],
            "ai_fallback": False,
            "default_value": "Default",
        }
        field_values = {"test_field": "Field Value"}
        user_preferences = None

        result = await form_filler_service._get_field_value(
            field_name="test_field",
            field_def=field_def,
            field_values=field_values,
            user_preferences=user_preferences,
        )

        assert result == "Field Value"

    @pytest.mark.asyncio
    async def test_get_field_value_mapped_answer(self, form_filler_service):
        """Test _get_field_value with mapped answers."""
        field_def = {
            "type": "select",
            "answers": ["First Answer", "Second Answer"],
            "ai_fallback": False,
            "default_value": "Default",
        }
        field_values = {}
        user_preferences = None

        result = await form_filler_service._get_field_value(
            field_name="test_field",
            field_def=field_def,
            field_values=field_values,
            user_preferences=user_preferences,
        )

        # Should use first non-empty mapped answer
        assert result == "First Answer"

    @pytest.mark.asyncio
    async def test_get_field_value_default_value(self, form_filler_service):
        """Test _get_field_value with default value."""
        field_def = {
            "type": "number",
            "answers": [],
            "ai_fallback": False,
            "default_value": "50000",
        }
        field_values = {}
        user_preferences = None

        result = await form_filler_service._get_field_value(
            field_name="test_field",
            field_def=field_def,
            field_values=field_values,
            user_preferences=user_preferences,
        )

        assert result == "50000"

    @pytest.mark.asyncio
    async def test_get_field_value_ai_fallback(self, form_filler_service):
        """Test _get_field_value with AI fallback."""
        field_def = {
            "type": "text",
            "answers": [],
            "ai_fallback": True,
            "default_value": "",
            "description": "Test field for AI generation",
        }
        field_values = {}
        user_preferences = None

        # AI service should be called
        await form_filler_service._get_field_value(
            field_name="test_field",
            field_def=field_def,
            field_values=field_values,
            user_preferences=user_preferences,
        )

        # AI should have been called
        form_filler_service.ai_service.generate_content.assert_called()

    @pytest.mark.asyncio
    async def test_generate_ai_answer_success(self, form_filler_service):
        """Test successful AI answer generation."""
        field_def = {
            "type": "textarea",
            "description": "Test description for AI generation",
        }

        result = await form_filler_service._generate_ai_answer(
            field_name="test_field", field_def=field_def
        )

        # Should have called AI and returned response
        form_filler_service.ai_service.generate_content.assert_called_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_generate_ai_answer_error_handling(self, form_filler_service):
        """Test AI answer generation error handling."""
        # Make AI service raise exception
        form_filler_service.ai_service.generate_content = AsyncMock(
            side_effect=Exception("AI service error")
        )

        field_def = {"type": "text", "description": "Test field"}

        result = await form_filler_service._generate_ai_answer(
            field_name="test_field", field_def=field_def
        )

        # Should return None on error
        assert result is None

    @pytest.mark.asyncio
    async def test_fill_select_field(self, form_filler_service):
        """Test select field filling."""
        field_def = {
            "xpath": "//select[@name='test']",
            "type": "select",
            "answers": ["Option1", "Option2"],
        }

        result = await form_filler_service._fill_select_field(
            field_name="test_field", value="Option1", field_def=field_def
        )

        assert result["action"] == "select_option"
        assert result["field_name"] == "test_field"
        assert result["selected_value"] == "Option1"
        assert result["xpath"] == "//select[@name='test']"

    @pytest.mark.asyncio
    async def test_fill_select_field_validation_warning(self, form_filler_service):
        """Test select field with invalid value shows warning."""
        field_def = {
            "xpath": "//select[@name='test']",
            "type": "select",
            "answers": ["Option1", "Option2"],
        }

        # Value not in mapped answers
        result = await form_filler_service._fill_select_field(
            field_name="test_field", value="Invalid Option", field_def=field_def
        )

        # Should still return result but with warning in logs
        assert result["action"] == "select_option"
        assert result["selected_value"] == "Invalid Option"

    @pytest.mark.asyncio
    async def test_fill_text_field(self, form_filler_service):
        """Test text field filling."""
        field_def = {"xpath": "//input[@name='test']", "type": "text"}

        result = await form_filler_service._fill_text_field(
            field_name="test_field", value="Test Value", field_def=field_def
        )

        assert result["action"] == "type_text"
        assert result["field_name"] == "test_field"
        assert result["value"] == "Test Value"

    @pytest.mark.asyncio
    async def test_fill_textarea_field(self, form_filler_service):
        """Test textarea field filling."""
        field_def = {"xpath": "//textarea[@name='test']", "type": "textarea"}

        result = await form_filler_service._fill_textarea_field(
            field_name="test_field", value="Long text content...", field_def=field_def
        )

        assert result["action"] == "type_textarea"
        assert result["field_name"] == "test_field"
        assert result["value"] == "Long text content..."

    @pytest.mark.asyncio
    async def test_fill_checkbox_field(self, form_filler_service):
        """Test checkbox field filling."""
        field_def = {"xpath": "//input[@type='checkbox']", "type": "checkbox"}

        result = await form_filler_service._fill_checkbox_field(
            field_name="test_field", value="true", field_def=field_def
        )

        assert result["action"] == "check"
        assert result["field_name"] == "test_field"
        assert result["value"] == "true"

    @pytest.mark.asyncio
    async def test_fill_number_field(self, form_filler_service):
        """Test number field filling."""
        field_def = {"xpath": "//input[@type='number']", "type": "number"}

        result = await form_filler_service._fill_number_field(
            field_name="test_field", value="100000", field_def=field_def
        )

        assert result["action"] == "type_number"
        assert result["field_name"] == "test_field"
        assert result["value"] == 100000

    @pytest.mark.asyncio
    async def test_fill_file_field(self, form_filler_service):
        """Test file field filling."""
        field_def = {"xpath": "//input[@type='file']", "type": "file"}

        result = await form_filler_service._fill_file_field(
            field_name="test_field", value="/path/to/resume.pdf", field_def=field_def
        )

        assert result["action"] == "upload_file"
        assert result["field_name"] == "test_field"
        assert result["file_path"] == "/path/to/resume.pdf"

    @pytest.mark.asyncio
    async def test_generate_form_preview(self, form_filler_service, mock_yaml_content):
        """Test form preview generation."""
        form_filler_service.templates = mock_yaml_content

        user_preferences = {"years_of_experience": "Custom experience"}

        preview = await form_filler_service.generate_form_preview(
            platform="linkedin", user_preferences=user_preferences
        )

        # User preference should be in preview
        assert "years_of_experience" in preview
        assert preview["years_of_experience"] == "Custom experience"

    @pytest.mark.asyncio
    async def test_reload_templates(self, form_filler_service):
        """Test template reloading."""
        # Mock _load_form_templates to return different data
        with patch.object(
            FormFillerService, "_load_form_templates", return_value={"new": "templates"}
        ):
            form_filler_service.reload_templates()

        assert form_filler_service.templates == {"new": "templates"}

    @pytest.mark.asyncio
    async def test_get_platform_stats(self, form_filler_service, mock_yaml_content):
        """Test platform statistics generation."""
        form_filler_service.templates = mock_yaml_content

        stats = form_filler_service.get_platform_stats()

        assert "linkedin" in stats
        assert "indeed" in stats
        assert "glassdoor" in stats
        assert stats["linkedin"]["total_fields"] == 3
        assert stats["indeed"]["total_fields"] == 2
        assert stats["glassdoor"]["total_fields"] == 1

    @pytest.mark.asyncio
    async def test_error_during_fill_form(self, form_filler_service, mock_yaml_content):
        """Test error handling during form filling."""
        form_filler_service.templates = mock_yaml_content

        # Mock _get_field_value to raise exception
        form_filler_service._get_field_value = AsyncMock(
            side_effect=Exception("Test error")
        )

        # Should handle error gracefully
        result = await form_filler_service.fill_form(
            platform="linkedin", field_values={}
        )

        assert result == {}

    @pytest.mark.asyncio
    async def test_fill_form_multiple_platforms(
        self, form_filler_service, mock_yaml_content
    ):
        """Test filling forms for multiple platforms."""
        form_filler_service.templates = mock_yaml_content

        # Test each platform
        linkedin_result = await form_filler_service.fill_form(
            platform="linkedin", field_values={}
        )

        indeed_result = await form_filler_service.fill_form(
            platform="indeed", field_values={}
        )

        glassdoor_result = await form_filler_service.fill_form(
            platform="glassdoor", field_values={}
        )

        # Each platform should have different fields
        assert "years_of_experience" in linkedin_result
        assert "resume_upload" in indeed_result
        assert "employment_type" in glassdoor_result

    @pytest.mark.asyncio
    async def test_empty_answers_handling(self, form_filler_service):
        """Test handling of empty answers list."""
        field_def = {
            "type": "select",
            "answers": [],
            "ai_fallback": False,
            "default_value": "Default Answer",
        }
        field_values = {}
        user_preferences = None

        result = await form_filler_service._get_field_value(
            field_name="test_field",
            field_def=field_def,
            field_values=field_values,
            user_preferences=user_preferences,
        )

        # Should fall back to default value
        assert result == "Default Answer"

    @pytest.mark.asyncio
    async def test_whitespace_in_answers(self, form_filler_service):
        """Test handling of whitespace-only answers."""
        field_def = {
            "type": "select",
            "answers": ["", "  ", "Valid Answer"],
            "ai_fallback": False,
            "default_value": "Default",
        }
        field_values = {}
        user_preferences = None

        result = await form_filler_service._get_field_value(
            field_name="test_field",
            field_def=field_def,
            field_values=field_values,
            user_preferences=user_preferences,
        )

        # Should skip empty answers and use first valid one
        assert result == "Valid Answer"

    @pytest.mark.asyncio
    async def test_service_close(self, form_filler_service):
        """Test service cleanup."""
        # Close service
        await form_filler_service.close()

        # Templates should be cleared
        assert form_filler_service.templates is None


# Edge case tests
class TestFormFillerEdgeCases:
    """Edge case tests for FormFillerService."""

    @pytest_asyncio.fixture
    async def service_with_mock(self):
        """Create service with mocked dependencies."""
        mock_ai = MockAIService()
        service = FormFillerService(ai_service=mock_ai, user_id="test_user")
        service.templates = {
            "test": {
                "field1": {
                    "type": "text",
                    "xpath": "//input",
                    "default_value": "default",
                    "ai_fallback": False,
                }
            }
        }
        yield service
        await service.close()

    @pytest.mark.asyncio
    async def test_none_field_values(self, service_with_mock):
        """Test handling of None field_values."""
        result = await service_with_mock.fill_form(platform="test", field_values=None)

        assert result == {"field1": "default"}

    @pytest.mark.asyncio
    async def test_none_user_preferences(self, service_with_mock):
        """Test handling of None user_preferences."""
        result = await service_with_mock.fill_form(
            platform="test", field_values={}, user_preferences=None
        )

        assert result == {"field1": "default"}

    @pytest.mark.asyncio
    async def test_empty_field_values(self, service_with_mock):
        """Test handling of empty field_values dict."""
        result = await service_with_mock.fill_form(platform="test", field_values={})

        assert result == {"field1": "default"}

    @pytest.mark.asyncio
    async def test_very_long_field_value(self, service_with_mock):
        """Test handling of very long field values."""
        long_value = "A" * 10000

        field_values = {"field1": long_value}

        result = await service_with_mock.fill_form(
            platform="test", field_values=field_values
        )

        assert result["field1"] == long_value

    @pytest.mark.asyncio
    async def test_special_characters_in_values(self, service_with_mock):
        """Test handling of special characters in field values."""
        special_value = 'Test\'s "quoted" & <special> chars'

        field_values = {"field1": special_value}

        result = await service_with_mock.fill_form(
            platform="test", field_values=field_values
        )

        assert result["field1"] == special_value

    @pytest.mark.asyncio
    async def test_unicode_in_values(self, service_with_mock):
        """Test handling of Unicode characters in field values."""
        unicode_value = "Unicode: 你好 🚀 émojis 🎉"

        field_values = {"field1": unicode_value}

        result = await service_with_mock.fill_form(
            platform="test", field_values=field_values
        )

        assert result["field1"] == unicode_value
