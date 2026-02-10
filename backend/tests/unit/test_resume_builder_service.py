"""Unit tests for resume builder service."""

import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from src.services.resume_builder_service import (
    ResumeBuilderService,
    ProfileData,
    ResumeOptions,
    ResumeFormat,
    ResumeTemplate,
)


class TestResumeTemplate:
    """Test cases for ResumeTemplate enum."""

    def test_resume_template_values(self) -> None:
        """ResumeTemplate should have expected string values."""
        assert ResumeTemplate.MODERN.value == "modern"
        assert ResumeTemplate.PROFESSIONAL.value == "professional"
        assert ResumeTemplate.MINIMALIST.value == "minimalist"
        assert ResumeTemplate.CREATIVE.value == "creative"
        assert ResumeTemplate.TECHNICAL.value == "technical"


class TestResumeFormat:
    """Test cases for ResumeFormat enum."""

    def test_resume_format_values(self) -> None:
        """ResumeFormat should have expected string values."""
        assert ResumeFormat.PDF.value == "pdf"
        assert ResumeFormat.DOCX.value == "docx"
        assert ResumeFormat.HTML.value == "html"


class TestProfileData:
    """Test cases for ProfileData model."""

    def test_profile_data_minimal(self) -> None:
        """Test creating profile data with minimal fields."""
        profile = ProfileData(
            full_name="John Doe",
            email="john@example.com",
        )

        assert profile.full_name == "John Doe"
        assert profile.email == "john@example.com"
        assert profile.skills == []

    def test_profile_data_with_experience(self) -> None:
        """Test creating profile data with experience."""
        profile = ProfileData(
            full_name="Jane Smith",
            email="jane@example.com",
            experience=[
                {
                    "title": "Software Engineer",
                    "company": "TechCorp",
                    "start_date": "2022-01",
                    "end_date": None,
                    "description": "Built cool stuff",
                }
            ],
        )

        assert len(profile.experience) == 1
        assert profile.experience[0]["title"] == "Software Engineer"


class TestResumeOptions:
    """Test cases for ResumeOptions model."""

    def test_resume_options_defaults(self) -> None:
        """Test default resume options."""
        options = ResumeOptions()

        assert options.template == ResumeTemplate.MODERN
        assert options.format == ResumeFormat.PDF
        assert options.include_photo is False
        assert options.color_theme == "blue"

    def test_resume_options_custom(self) -> None:
        """Test resume options with custom values."""
        options = ResumeOptions(
            template=ResumeTemplate.CREATIVE,
            format=ResumeFormat.HTML,
            include_photo=True,
            color_theme="green",
        )

        assert options.template == ResumeTemplate.CREATIVE
        assert options.format == ResumeFormat.HTML
        assert options.include_photo is True
        assert options.color_theme == "green"


@pytest.fixture
def resume_builder_service() -> ResumeBuilderService:
    """Provide a resume builder service."""
    return ResumeBuilderService()


def test_templates_directory_exists(
    resume_builder_service: ResumeBuilderService,
) -> None:
    """Templates directory should exist."""
    assert resume_builder_service.templates_dir.exists()


def test_output_directory_created(
    resume_builder_service: ResumeBuilderService,
) -> None:
    """Output directory should be created."""
    assert resume_builder_service.output_dir.exists()


def test_jinja_environment_initialized(
    resume_builder_service: ResumeBuilderService,
) -> None:
    """Jinja2 environment should be initialized."""
    assert resume_builder_service.jinja_env is not None
