"""Career insights models."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CareerInsightsRequest(BaseModel):
    """Request model for generating career insights."""
    application_history: List[Dict[str, Any]] = Field(..., description="List of past job applications with status and details")
    skills: List[str] = Field(..., description="List of candidate's skills")
    experience_level: Optional[str] = Field(None, description="Current experience level")
    career_goals: Optional[str] = Field(None, description="Candidate's career goals")


class CareerInsightsResponse(BaseModel):
    """Response model for career insights."""
    market_analysis: str = Field(..., description="Analysis of the current job market relevant to the candidate")
    salary_insights: Dict[str, Any] = Field(..., description="Salary estimation and trends")
    recommended_roles: List[str] = Field(..., description="List of recommended roles to apply for")
    skill_gaps: List[str] = Field(..., description="Skills to acquire for career growth")
    strategic_advice: List[str] = Field(..., description="Actionable advice for career advancement")
    confidence_score: float = Field(..., description="Confidence score of the AI analysis")
