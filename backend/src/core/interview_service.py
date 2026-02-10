"""Interview preparation service interface."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class InterviewPrepCreate(BaseModel):
    """Data for creating an interview preparation reminder."""

    application_id: str
    interview_date: datetime
    notes: Optional[str] = None


class InterviewPrepUpdate(BaseModel):
    """Data for updating an interview preparation reminder."""

    status: Optional[str] = None
    notes: Optional[str] = None
    completed: Optional[bool] = None


class InterviewPrepResponse(BaseModel):
    """Interview preparation reminder response."""

    id: str
    application_id: str
    user_id: str
    interview_date: datetime
    notes: Optional[str]
    status: str
    completed: bool
    created_at: datetime
    updated_at: datetime


class InterviewPrepService(ABC):
    """Abstract interface for interview preparation services."""

    @abstractmethod
    async def create_prep(
        self, user_id: str, prep_data: InterviewPrepCreate
    ) -> InterviewPrepResponse:
        """
        Create a new interview preparation reminder.

        Args:
            user_id: User ID
            prep_data: Interview prep data

        Returns:
            Created interview prep response
        """
        pass

    @abstractmethod
    async def get_upcoming_preps(
        self, user_id: str, days_ahead: int = 7
    ) -> List[InterviewPrepResponse]:
        """
        Get upcoming interview preparations.

        Args:
            user_id: User ID
            days_ahead: Number of days to look ahead

        Returns:
            List of upcoming interview preps
        """
        pass

    @abstractmethod
    async def update_prep(
        self, prep_id: str, user_id: str, update_data: InterviewPrepUpdate
    ) -> Optional[InterviewPrepResponse]:
        """
        Update an interview preparation.

        Args:
            prep_id: Interview prep ID
            user_id: User ID (for authorization)
            update_data: Update data

        Returns:
            Updated interview prep or None if not found
        """
        pass

    @abstractmethod
    async def delete_prep(self, prep_id: str, user_id: str) -> bool:
        """
        Delete an interview preparation.

        Args:
            prep_id: Interview prep ID
            user_id: User ID (for authorization)

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    async def get_prep_by_id(
        self, prep_id: str, user_id: str
    ) -> Optional[InterviewPrepResponse]:
        """
        Get an interview preparation by ID.

        Args:
            prep_id: Interview prep ID
            user_id: User ID (for authorization)

        Returns:
            Interview prep or None if not found
        """
        pass
