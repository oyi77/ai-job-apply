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
    config_id: str
    job_id: str
    job_title: str
    company: str
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True
