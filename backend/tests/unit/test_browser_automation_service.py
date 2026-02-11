"""Unit tests for browser automation service."""

import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

# Ensure `src` package is importable when running tests without installing the
# project into the current environment.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from src.services.browser_automation_service import (
    BrowserManager,
    FormFieldDetector,
    BrowserAutomationService,
    LinkedInHandler,
    IndeedHandler,
    GlassdoorHandler,
)
from src.models.application import (
    ApplicationUpdateRequest,  # Fixed: was ApplicationCreateRequest
    ApplicationCreateRequest,
    AutomationConfig,
)


class TestBrowserManager:
    """Test cases for BrowserManager class."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for testing."""
        config = MagicMock()
        config.HEADLESS = True
        config.ANT_DETECTION = True
        config.HUMANIZE = True
        config.DEFAULT_TIMEOUT = 30
        return config

    @pytest.mark.asyncio
    async def test_browser_manager_initialization(self, mock_config):
        """Test BrowserManager initializes with correct settings."""
        with patch("src.services.browser_automation_service.config", mock_config):
            manager = BrowserManager()
            assert manager.headless is True
            assert manager.anti_detection is True
            assert manager.humanize is True
            assert manager.timeout == 30

    @pytest.mark.asyncio
    async def test_browser_manager_context_manager(self, mock_config):
        """Test BrowserManager can be used as context manager."""
        with patch("src.services.browser_automation_service.config", mock_config):
            with patch(
                "src.services.browser_automation_service.async_playwright"
            ) as mock_playwright:
                mock_browser = AsyncMock()
                mock_context = AsyncMock()
                mock_page = AsyncMock()

                mock_browser.contexts = [mock_context]
                mock_context.pages = [mock_page]
                mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser

                async with BrowserManager() as browser:
                    assert browser is not None

    @pytest.mark.asyncio
    async def test_browser_manager_stealth_settings(self, mock_config):
        """Test BrowserManager applies stealth settings."""
        with patch("src.services.browser_automation_service.config", mock_config):
            manager = BrowserManager()

            mock_page = MagicMock()
            mock_page.add_init_script = AsyncMock()

            await manager._apply_stealth_settings(mock_page)

            # Verify stealth scripts were added
            assert mock_page.add_init_script.called


class TestFormFieldDetector:
    """Test cases for FormFieldDetector class."""

    @pytest.fixture
    def detector(self):
        """Create FormFieldDetector instance."""
        return FormFieldDetector()

    @pytest.mark.asyncio
    async def test_detect_fields_empty_page(self, detector):
        """Test field detection on empty page."""
        mock_page = MagicMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])

        fields = await detector.detect_fields(mock_page)

        assert fields == {}

    @pytest.mark.asyncio
    async def test_detect_input_fields(self, detector):
        """Test detection of input fields."""
        mock_page = MagicMock()
        mock_page.query_selector_all = AsyncMock(
            return_value=[
                MagicMock(
                    get_attribute=AsyncMock(
                        side_effect=lambda attr: {
                            "name": "email",
                            "type": "email",
                            "id": "email-field",
                            "placeholder": "Enter your email",
                        }.get(attr)
                    )
                ),
                MagicMock(
                    get_attribute=AsyncMock(
                        side_effect=lambda attr: {
                            "name": "password",
                            "type": "password",
                            "id": "password-field",
                        }.get(attr)
                    )
                ),
            ]
        )

        fields = await detector.detect_fields(mock_page)

        assert "email" in fields
        assert "password" in fields

    @pytest.mark.asyncio
    async def test_detect_textarea_fields(self, detector):
        """Test detection of textarea fields."""
        mock_page = MagicMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.query_selector_all = AsyncMock(
            return_value=[
                MagicMock(
                    get_attribute=AsyncMock(
                        side_effect=lambda attr: {
                            "name": "cover_letter",
                            "tag_name": "TEXTAREA",
                        }.get(attr)
                    )
                ),
            ]
        )

        fields = await detector.detect_fields(mock_page)

        assert "cover_letter" in fields

    @pytest.mark.asyncio
    async def test_map_resume_data_to_fields(self, detector):
        """Test mapping resume data to form fields."""
        mock_page = MagicMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])

        resume_data = {
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "resume_text": "My resume content...",
        }

        # Mock form fields
        detector._form_fields = {
            "name": {"element": MagicMock(), "type": "text"},
            "email": {"element": MagicMock(), "type": "email"},
            "phone": {"element": MagicMock(), "type": "tel"},
        }

        mapping = await detector.map_resume_data_to_fields(mock_page, resume_data)

        assert "name" in mapping
        assert "email" in mapping
        assert "phone" in mapping


class TestLinkedInHandler:
    """Test cases for LinkedInHandler class."""

    @pytest.fixture
    def handler(self):
        """Create LinkedInHandler instance."""
        return LinkedInHandler()

    def test_handler_name(self, handler):
        """Test handler has correct platform name."""
        assert handler.platform_name == "linkedin"

    @pytest.mark.asyncio
    async def test_detect_easy_apply_button_not_found(self, handler):
        """Test detection when Easy Apply button is not found."""
        mock_page = MagicMock()
        mock_page.query_selector = AsyncMock(return_value=None)

        result = await handler._detect_easy_apply_button(mock_page)

        assert result is False

    @pytest.mark.asyncio
    async def test_detect_easy_apply_button_found(self, handler):
        """Test detection when Easy Apply button is found."""
        mock_page = MagicMock()
        mock_page.query_selector = AsyncMock(return_value=MagicMock())

        result = await handler._detect_easy_apply_button(mock_page)

        assert result is True

    @pytest.mark.asyncio
    async def test_handle_easy_apply_no_button(self, handler):
        """Test handling when Easy Apply button is not present."""
        mock_page = MagicMock()
        mock_page.query_selector = AsyncMock(return_value=None)

        result = await handler.handle_apply(mock_page, {})

        # Should return fallback to external URL
        assert result["success"] is False
        assert "external_url" in result


class TestIndeedHandler:
    """Test cases for IndeedHandler class."""

    @pytest.fixture
    def handler(self):
        """Create IndeedHandler instance."""
        return IndeedHandler()

    def test_handler_name(self, handler):
        """Test handler has correct platform name."""
        assert handler.platform_name == "indeed"

    @pytest.mark.asyncio
    async def test_detect_application_form_not_found(self, handler):
        """Test detection when application form is not found."""
        mock_page = MagicMock()
        mock_page.query_selector = AsyncMock(return_value=None)

        result = await handler._detect_application_form(mock_page)

        assert result is False

    @pytest.mark.asyncio
    async def test_handle_application_form_not_found(self, handler):
        """Test handling when application form is not found."""
        mock_page = MagicMock()
        mock_page.query_selector = AsyncMock(return_value=None)

        result = await handler.handle_apply(mock_page, {})

        # Should return fallback to external URL
        assert result["success"] is False
        assert "external_url" in result


class TestGlassdoorHandler:
    """Test cases for GlassdoorHandler class."""

    @pytest.fixture
    def handler(self):
        """Create GlassdoorHandler instance."""
        return GlassdoorHandler()

    def test_handler_name(self, handler):
        """Test handler has correct platform name."""
        assert handler.platform_name == "glassdoor"

    @pytest.mark.asyncio
    async def test_detect_apply_button_not_found(self, handler):
        """Test detection when apply button is not found."""
        mock_page = MagicMock()
        mock_page.query_selector = AsyncMock(return_value=None)

        result = await handler._detect_apply_button(mock_page)

        assert result is False

    @pytest.mark.asyncio
    async def test_handle_apply_button_not_found(self, handler):
        """Test handling when apply button is not found."""
        mock_page = MagicMock()
        mock_page.query_selector = AsyncMock(return_value=None)

        result = await handler.handle_apply(mock_page, {})

        # Should return fallback to external URL
        assert result["success"] is False
        assert "external_url" in result


class TestBrowserAutomationService:
    """Test cases for BrowserAutomationService class."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for testing."""
        config = MagicMock()
        config.HEADLESS = True
        config.ANT_DETECTION = True
        config.HUMANIZE = True
        config.DEFAULT_TIMEOUT = 30
        config.MAX_RETRIES = 3
        config.RETRY_DELAY = 1
        return config

    @pytest.fixture
    def automation_service(self, mock_config):
        """Create BrowserAutomationService with mocked dependencies."""
        with patch("src.services.browser_automation_service.config", mock_config):
            return BrowserAutomationService()

    @pytest.mark.asyncio
    async def test_service_initialization(self, automation_service):
        """Test service initializes correctly."""
        assert automation_service is not None
        assert hasattr(automation_service, "browser_manager")
        assert hasattr(automation_service, "field_detector")
        assert hasattr(automation_service, "handlers")

    @pytest.mark.asyncio
    async def test_get_handler_for_platform(self, automation_service):
        """Test getting handler for specific platform."""
        linkedin_handler = automation_service.get_handler("linkedin")
        assert linkedin_handler is not None
        assert isinstance(linkedin_handler, LinkedInHandler)

        indeed_handler = automation_service.get_handler("indeed")
        assert indeed_handler is not None
        assert isinstance(indeed_handler, IndeedHandler)

        glassdoor_handler = automation_service.get_handler("glassdoor")
        assert glassdoor_handler is not None
        assert isinstance(glassdoor_handler, GlassdoorHandler)

    @pytest.mark.asyncio
    async def test_get_handler_unknown_platform(self, automation_service):
        """Test getting handler for unknown platform returns None."""
        handler = automation_service.get_handler("unknown_platform")
        assert handler is None

    @pytest.mark.asyncio
    async def test_apply_to_job_linkedin_easy_apply(self, automation_service):
        """Test applying to LinkedIn job with Easy Apply."""
        with patch.object(
            automation_service.browser_manager, "start_browser", new_callable=AsyncMock
        ):
            with patch.object(
                automation_service.browser_manager,
                "close_browser",
                new_callable=AsyncMock,
            ):
                mock_page = MagicMock()
                automation_service.browser_manager.current_page = mock_page

                mock_handler = AsyncMock()
                mock_handler.handle_apply = AsyncMock(
                    return_value={
                        "success": True,
                        "application_id": "app_123",
                        "platform": "linkedin",
                    }
                )

                request = ApplicationCreateRequest(
                    job_id="job_123",
                    job_url="https://www.linkedin.com/jobs/view/test",
                    resume_id="resume_123",
                    cover_letter_id=None,
                    additional_data={"platform": "linkedin"},
                    config=AutomationConfig(headless=True, timeout=30, humanize=True),
                )

                result = await automation_service.apply_to_job(
                    request, handler=mock_handler
                )

                assert result["success"] is True
                assert result["application_id"] == "app_123"

    @pytest.mark.asyncio
    async def test_apply_to_job_external_fallback(self, automation_service):
        """Test applying when platform requires external URL."""
        with patch.object(
            automation_service.browser_manager, "start_browser", new_callable=AsyncMock
        ):
            with patch.object(
                automation_service.browser_manager,
                "close_browser",
                new_callable=AsyncMock,
            ):
                mock_page = MagicMock()
                automation_service.browser_manager.current_page = mock_page

                mock_handler = AsyncMock()
                mock_handler.handle_apply = AsyncMock(
                    return_value={
                        "success": False,
                        "external_url": "https://careers.google.com/jobs/123",
                        "platform": "linkedin",
                    }
                )

                request = ApplicationCreateRequest(
                    job_id="job_123",
                    job_url="https://www.linkedin.com/jobs/view/test",
                    resume_id="resume_123",
                    cover_letter_id=None,
                    additional_data={"platform": "linkedin"},
                    config=AutomationConfig(headless=True, timeout=30, humanize=True),
                )

                result = await automation_service.apply_to_job(
                    request, handler=mock_handler
                )

                assert result["success"] is False
                assert "external_url" in result

    @pytest.mark.asyncio
    async def test_close_cleanup(self, automation_service):
        """Test service cleanup closes browser."""
        with patch.object(
            automation_service.browser_manager, "close_browser", new_callable=AsyncMock
        ) as mock_close:
            await automation_service.close()

            mock_close.assert_called_once()


class TestHumanizeActions:
    """Test cases for human-like action patterns."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for testing."""
        config = MagicMock()
        config.HUMANIZE = True
        return config

    @pytest.mark.asyncio
    async def test_random_delay_between_actions(self, mock_config):
        """Test that random delays are applied between actions."""
        with patch("src.services.browser_automation_service.config", mock_config):
            manager = BrowserManager()

            delays = []
            for _ in range(10):
                delay = manager._random_delay(0.1, 0.5)
                delays.append(delay)
                assert 0.1 <= delay <= 0.5

    @pytest.mark.asyncio
    async def test_human_like_scroll(self, mock_config):
        """Test human-like scrolling pattern."""
        with patch("src.services.browser_automation_service.config", mock_config):
            manager = BrowserManager()

            mock_page = MagicMock()
            mock_page.evaluate = AsyncMock(return_value=1000)

            # Should perform multiple small scrolls
            await manager._human_like_scroll(mock_page)

            # Verify scroll was called multiple times
            assert mock_page.evaluate.called
