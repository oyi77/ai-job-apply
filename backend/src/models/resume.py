"""Resume-related data models."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pathlib import Path


class Resume(BaseModel):
    """Resume model."""
    id: Optional[str] = None
    name: str = Field(..., description="Resume name")
    file_path: str = Field(..., description="Path to resume file")
    file_type: str = Field(..., description="File type (pdf, docx, etc.)")
    content: Optional[str] = Field(None, description="Extracted text content")
    skills: Optional[List[str]] = Field(None, description="Skills extracted from resume")
    experience_years: Optional[int] = Field(None, description="Years of experience")
    education: Optional[List[str]] = Field(None, description="Education information")
    certifications: Optional[List[str]] = Field(None, description="Certifications")
    is_default: bool = Field(default=False, description="Whether this is the default resume")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = Field(None, description="ID of the user who owns this resume")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
    
    @property
    def file_size(self) -> Optional[int]:
        """Get file size in bytes."""
        try:
            return Path(self.file_path).stat().st_size if Path(self.file_path).exists() else None
        except (OSError, ValueError):
            return None
    
    @property
    def exists(self) -> bool:
        """Check if resume file exists."""
        return Path(self.file_path).exists()


class ResumeOptimizationRequest(BaseModel):
    """Resume optimization request model."""
    resume_id: str = Field(..., description="Resume ID to optimize")
    job_description: str = Field(..., description="Target job description")
    target_role: str = Field(..., description="Target job role")
    company_name: Optional[str] = Field(None, description="Target company name")
    optimization_focus: Optional[List[str]] = Field(None, description="Areas to focus optimization on")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "resume_id": "res_123",
                "job_description": "We are looking for a Python developer...",
                "target_role": "Senior Python Developer",
                "company_name": "TechCorp Inc.",
                "optimization_focus": ["skills", "experience", "achievements"]
            }
        }
    }


class ResumeOptimizationResponse(BaseModel):
    """Resume optimization response model with ATS scoring."""
    original_resume: Resume = Field(..., description="Original resume")
    optimized_content: str = Field(..., description="Optimized resume content")
    suggestions: List[str] = Field(..., description="Optimization suggestions")
    skill_gaps: List[str] = Field(default_factory=list, description="Identified skill gaps")
    improvements: List[str] = Field(default_factory=list, description="Specific improvements")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Optimization confidence score")
    ats_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="ATS compatibility score (0-1)")
    ats_checks: Optional[Dict[str, float]] = Field(None, description="Individual ATS check scores")
    ats_recommendations: Optional[List[str]] = Field(None, description="ATS-specific recommendations")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class BulkDeleteRequest(BaseModel):
    """Bulk deletion request model."""
    ids: List[str] = Field(..., description="List of IDs to delete")
