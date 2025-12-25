"""Cover letter data models."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class CoverLetterRequest(BaseModel):
    """Cover letter generation request model."""
    job_title: str = Field(..., description="Target job title")
    company_name: str = Field(..., description="Target company name")
    job_description: str = Field(..., description="Job description")
    resume_summary: str = Field(..., description="Resume summary for personalization")
    tone: str = Field(default="professional", description="Desired tone (professional, friendly, confident)")
    focus_areas: Optional[list[str]] = Field(None, description="Areas to emphasize")
    custom_instructions: Optional[str] = Field(None, description="Custom instructions for generation")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "job_title": "Senior Python Developer",
                "company_name": "TechCorp Inc.",
                "job_description": "We are looking for a Python developer...",
                "resume_summary": "Experienced Python developer with 5 years...",
                "tone": "professional",
                "focus_areas": ["technical skills", "leadership", "innovation"],
                "custom_instructions": "Emphasize experience with cloud technologies"
            }
        }
    }


class CoverLetterCreate(BaseModel):
    """Cover letter creation model."""
    job_title: str = Field(..., description="Target job title")
    company_name: str = Field(..., description="Target company name")
    content: str = Field(..., description="Cover letter content")
    file_path: Optional[str] = Field(None, description="Path to saved cover letter file")
    tone: str = Field(default="professional", description="Tone used in generation")
    word_count: Optional[int] = Field(None, description="Number of words in cover letter")
    generated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="When cover letter was generated")
    
    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True
    )


class CoverLetterUpdate(BaseModel):
    """Cover letter update model."""
    job_title: Optional[str] = Field(None, description="Target job title")
    company_name: Optional[str] = Field(None, description="Target company name")
    content: Optional[str] = Field(None, description="Cover letter content")
    file_path: Optional[str] = Field(None, description="Path to saved cover letter file")
    tone: Optional[str] = Field(None, description="Tone used in generation")
    word_count: Optional[int] = Field(None, description="Number of words in cover letter")
    
    model_config = ConfigDict(
        populate_by_name=True
    )


class CoverLetter(BaseModel):
    """Cover letter model."""
    id: Optional[str] = None
    job_title: str = Field(..., description="Target job title")
    company_name: str = Field(..., description="Target company name")
    content: str = Field(..., description="Generated cover letter content")
    file_path: Optional[str] = Field(None, description="Path to saved cover letter file")
    tone: str = Field(..., description="Tone used in generation")
    word_count: int = Field(default=0, description="Number of words in cover letter")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(
        populate_by_name=True
    )
    
    @property
    def reading_time_minutes(self) -> float:
        """Estimate reading time in minutes (average 200 words per minute)."""
        return round(self.word_count / 200, 1)
