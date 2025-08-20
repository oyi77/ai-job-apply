"""Cover letter data models."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


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


class CoverLetter(BaseModel):
    """Cover letter model."""
    id: Optional[str] = None
    job_title: str = Field(..., description="Target job title")
    company_name: str = Field(..., description="Target company name")
    content: str = Field(..., description="Generated cover letter content")
    file_path: Optional[str] = Field(None, description="Path to saved cover letter file")
    tone: str = Field(..., description="Tone used in generation")
    word_count: int = Field(..., description="Number of words in cover letter")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
    
    @property
    def reading_time_minutes(self) -> float:
        """Estimate reading time in minutes (average 200 words per minute)."""
        return round(self.word_count / 200, 1)
