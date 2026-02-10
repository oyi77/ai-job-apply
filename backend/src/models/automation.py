from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AutoApplyConfigCreate(BaseModel):
    keywords: List[str]
    locations: List[str]
    min_salary: Optional[int] = None
    daily_limit: int = Field(default=5, le=50)


class AutoApplyConfigUpdate(BaseModel):
    keywords: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    min_salary: Optional[int] = None
    daily_limit: Optional[int] = Field(None, le=50)
    is_active: Optional[bool] = None


class AutoApplyConfig(AutoApplyConfigCreate):
    id: str
    user_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AutoApplyActivityLog(BaseModel):
    id: str
    user_id: str
    cycle_id: Optional[str] = None
    cycle_start: datetime
    cycle_end: Optional[datetime] = None
    cycle_status: str
    jobs_searched: int
    jobs_matched: int
    jobs_applied: int
    applications_successful: int
    applications_failed: int
    errors: Optional[str] = None
    screenshots: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
