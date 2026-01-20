"""Tests for email templates."""

import pytest
from src.services.email_templates import EmailTemplateRenderer, _sanitize_template_data


@pytest.fixture
def template_renderer() -> EmailTemplateRenderer:
    """Create a template renderer instance for testing."""
    return EmailTemplateRenderer()


class TestSanitizeTemplateData:
    """Tests for template data sanitization."""

    def test_sanitize_removes_suspicious_characters(self):
        """Test that suspicious characters are removed."""
        data = {
            "user_name": "Test{user}",
            "company": "Test@company[123]",
            "job_title": "Job<>title",
        }
        sanitized = _sanitize_template_data(data)

        # Check that suspicious characters are removed
        assert "{" not in sanitized["user_name"]
        assert "}" not in sanitized["user_name"]
        assert "@" not in sanitized["company"]
        assert "[" not in sanitized["company"]
        assert "]" not in sanitized["company"]
        assert "<" not in sanitized["job_title"]
        assert ">" not in sanitized["job_title"]

    def test_sanitize_preserves_safe_strings(self):
        """Test that safe strings are preserved."""
        data = {
            "user_name": "John Doe",
            "company": "Acme Inc.",
            "job_title": "Software Engineer",
        }
        sanitized = _sanitize_template_data(data)

        assert sanitized["user_name"] == "John Doe"
        assert sanitized["company"] == "Acme Inc."
        assert sanitized["job_title"] == "Software Engineer"

    def test_sanitize_handles_non_string_values(self):
        """Test that non-string values are preserved."""
        data = {
            "application_id": 12345,
            "expiry_hours": 24,
            "interview_date": None,
        }
        sanitized = _sanitize_template_data(data)

        assert sanitized["application_id"] == 12345
        assert sanitized["expiry_hours"] == 24
        assert sanitized["interview_date"] is None


class TestEmailTemplateRenderer:
    """Tests for email template rendering."""

    @pytest.mark.asyncio
    async def test_render_follow_up_reminder(
        self, template_renderer: EmailTemplateRenderer
    ):
        """Test rendering follow-up reminder template."""
        data = {
            "user_name": "John",
            "job_title": "Software Engineer",
            "company": "TechCorp",
            "application_id": "app_123",
            "app_url": "https://app.example.com",
        }

        subject, body_html, body_text = await template_renderer.render(
            "follow_up_reminder", data
        )

        assert "TechCorp" in subject
        assert "Software Engineer" in body_html
        assert "John" in body_html
        assert "https://app.example.com/applications/app_123" in body_html
        assert "Software Engineer" in body_text
        assert "John" in body_text

    @pytest.mark.asyncio
    async def test_render_status_check_reminder(
        self, template_renderer: EmailTemplateRenderer
    ):
        """Test rendering status check reminder template."""
        data = {
            "user_name": "Jane",
            "job_title": "Product Manager",
            "company": "StartupXYZ",
            "application_id": "app_456",
            "app_url": "https://app.example.com",
        }

        subject, body_html, body_text = await template_renderer.render(
            "status_check_reminder", data
        )

        assert "StartupXYZ" in subject
        assert "Jane" in body_html
        assert "Application Status Check" in body_html
        assert "Jane" in body_text

    @pytest.mark.asyncio
    async def test_render_interview_prep_reminder(
        self, template_renderer: EmailTemplateRenderer
    ):
        """Test rendering interview preparation reminder template."""
        data = {
            "user_name": "Alex",
            "job_title": "Data Scientist",
            "company": "BigData Co",
            "interview_date": "Monday, January 15th at 2:00 PM",
            "application_id": "app_789",
            "app_url": "https://app.example.com",
        }

        subject, body_html, body_text = await template_renderer.render(
            "interview_prep_reminder", data
        )

        assert "Data Scientist" in subject
        assert "BigData Co" in subject
        assert "Alex" in body_html
        assert "Interview Prep Reminder" in body_html
        assert "Monday, January 15th at 2:00 PM" in body_html
        assert "Alex" in body_text

    @pytest.mark.asyncio
    async def test_render_password_reset(
        self, template_renderer: EmailTemplateRenderer
    ):
        """Test rendering password reset template."""
        data = {
            "user_name": "Sam",
            "reset_link": "https://app.example.com/reset?token=abc123",
            "expiry_hours": 1,
        }

        subject, body_html, body_text = await template_renderer.render(
            "password_reset", data
        )

        assert "Reset" in subject
        assert "Sam" in body_html
        assert "https://app.example.com/reset?token=abc123" in body_html
        assert "1 hour" in body_html
        assert "Sam" in body_text
        assert "https://app.example.com/reset?token=abc123" in body_text

    @pytest.mark.asyncio
    async def test_render_application_confirmation(
        self, template_renderer: EmailTemplateRenderer
    ):
        """Test rendering application confirmation template."""
        data = {
            "user_name": "Chris",
            "job_title": "DevOps Engineer",
            "company": "CloudTech",
            "application_id": "app_999",
            "app_url": "https://app.example.com",
        }

        subject, body_html, body_text = await template_renderer.render(
            "application_confirmation", data
        )

        assert "DevOps Engineer" in subject
        assert "CloudTech" in subject
        assert "Chris" in body_html
        assert "Application Submitted" in body_html
        assert "Chris" in body_text

    @pytest.mark.asyncio
    async def test_render_welcome(self, template_renderer: EmailTemplateRenderer):
        """Test rendering welcome template."""
        data = {
            "user_name": "New User",
            "app_url": "https://app.example.com",
        }

        subject, body_html, body_text = await template_renderer.render("welcome", data)

        assert "Welcome" in subject
        assert "New User" in body_html
        assert "AI Job Application Assistant" in body_html
        assert "Smart Job Search" in body_html
        assert "New User" in body_text
        assert "Dashboard" in body_text

    @pytest.mark.asyncio
    async def test_render_unknown_template_raises_error(
        self, template_renderer: EmailTemplateRenderer
    ):
        """Test that rendering unknown template raises ValueError."""
        with pytest.raises(ValueError, match="Unknown template: nonexistent"):
            await template_renderer.render("nonexistent", {})

    @pytest.mark.asyncio
    async def test_render_with_minimal_data(
        self, template_renderer: EmailTemplateRenderer
    ):
        """Test rendering with minimal data uses defaults."""
        data = {}

        subject, body_html, body_text = await template_renderer.render(
            "follow_up_reminder", data
        )

        # Should use default values
        assert "the company" in subject
        assert "there" in body_html  # Default user_name
        assert "the position" in body_html  # Default job_title

    @pytest.mark.asyncio
    async def test_render_produces_html_and_text_versions(
        self, template_renderer: EmailTemplateRenderer
    ):
        """Test that render produces both HTML and text versions."""
        data = {
            "user_name": "Test User",
            "job_title": "Test Job",
            "company": "Test Company",
        }

        subject, body_html, body_text = await template_renderer.render(
            "follow_up_reminder", data
        )

        # HTML version should contain HTML tags
        assert "<html>" in body_html
        assert "<body>" in body_html
        assert "</html>" in body_html

        # Text version should NOT contain HTML tags
        assert "<html>" not in body_text
        assert "<body>" not in body_text
        assert "Test User" in body_text
        assert "Test Company" in body_text

    @pytest.mark.asyncio
    async def test_render_with_injection_attempt(
        self, template_renderer: EmailTemplateRenderer
    ):
        """Test that template injection attempts are sanitized."""
        data = {
            "user_name": "Test{__import__}",
            "job_title": "Job<script>alert('xss')</script>",
            "company": "Company${7*7}",
        }

        # Should not raise an error
        subject, body_html, body_text = await template_renderer.render(
            "follow_up_reminder", data
        )

        # The content should be sanitized
        assert "<script>" not in body_html
        assert "${7*7}" not in body_html


class TestTemplateRendererInit:
    """Tests for template renderer initialization."""

    def test_all_templates_registered(self):
        """Test that all expected templates are registered."""
        renderer = EmailTemplateRenderer()

        expected_templates = [
            "follow_up_reminder",
            "status_check_reminder",
            "interview_prep_reminder",
            "password_reset",
            "application_confirmation",
            "welcome",
        ]

        for template_name in expected_templates:
            assert template_name in renderer.templates

    def test_global_renderer_exists(self):
        """Test that global email_template_renderer exists."""
        from src.services.email_templates import email_template_renderer

        assert email_template_renderer is not None
        assert isinstance(email_template_renderer, EmailTemplateRenderer)
