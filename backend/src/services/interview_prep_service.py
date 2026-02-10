"""Interview preparation service implementation."""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.core.interview_service import (
    InterviewPrepCreate,
    InterviewPrepResponse,
    InterviewPrepService,
    InterviewPrepUpdate,
)
from src.database.repositories.application_repository import ApplicationRepository


logger = logging.getLogger(__name__)


class InterviewPrep:
    """Internal interview prep model."""

    def __init__(
        self,
        application_id: str,
        user_id: str,
        interview_date: datetime,
        notes: Optional[str] = None,
    ):
        self.id = f"prep_{uuid.uuid4().hex[:12]}"
        self.application_id = application_id
        self.user_id = user_id
        self.interview_date = interview_date
        self.notes = notes
        self.status = "scheduled"
        self.completed = False
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class InterviewPrepServiceImpl(InterviewPrepService):
    """Memory-based implementation of InterviewPrepService."""

    def __init__(self, application_repository: Optional[ApplicationRepository] = None):
        """
        Initialize the interview prep service.

        Args:
            application_repository: Optional application repository for validation
        """
        self._preps: Dict[str, InterviewPrep] = {}
        self._user_preps: Dict[str, List[str]] = {}  # user_id -> list of prep_ids
        self._application_repository = application_repository

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
        # Create the prep
        prep = InterviewPrep(
            application_id=prep_data.application_id,
            user_id=user_id,
            interview_date=prep_data.interview_date,
            notes=prep_data.notes,
        )

        # Store it
        self._preps[prep.id] = prep
        if user_id not in self._user_preps:
            self._user_preps[user_id] = []
        self._user_preps[user_id].append(prep.id)

        logger.info(f"Created interview prep: {prep.id} for user: {user_id}")

        return self._to_response(prep)

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
        now = datetime.utcnow()
        cutoff = now + timedelta(days=days_ahead)

        user_prep_ids = self._user_preps.get(user_id, [])
        upcoming = []

        for prep_id in user_prep_ids:
            prep = self._preps.get(prep_id)
            if prep and not prep.completed:
                if now <= prep.interview_date <= cutoff:
                    upcoming.append(self._to_response(prep))

        # Sort by interview date
        upcoming.sort(key=lambda x: x.interview_date)

        return upcoming

    async def update_prep(
        self,
        prep_id: str,
        user_id: str,
        update_data: InterviewPrepUpdate,
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
        prep = self._preps.get(prep_id)
        if not prep or prep.user_id != user_id:
            return None

        # Apply updates
        if update_data.status is not None:
            prep.status = update_data.status
        if update_data.notes is not None:
            prep.notes = update_data.notes
        if update_data.completed is not None:
            prep.completed = update_data.completed
            if update_data.completed:
                prep.status = "completed"

        prep.updated_at = datetime.utcnow()

        logger.info(f"Updated interview prep: {prep_id}")

        return self._to_response(prep)

    async def delete_prep(self, prep_id: str, user_id: str) -> bool:
        """
        Delete an interview preparation.

        Args:
            prep_id: Interview prep ID
            user_id: User ID (for authorization)

        Returns:
            True if deleted successfully
        """
        prep = self._preps.get(prep_id)
        if not prep or prep.user_id != user_id:
            return False

        # Remove from storage
        del self._preps[prep_id]
        if user_id in self._user_preps and prep_id in self._user_preps[user_id]:
            self._user_preps[user_id].remove(prep_id)

        logger.info(f"Deleted interview prep: {prep_id}")

        return True

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
        prep = self._preps.get(prep_id)
        if not prep or prep.user_id != user_id:
            return None

        return self._to_response(prep)

    def _to_response(self, prep: InterviewPrep) -> InterviewPrepResponse:
        """Convert internal model to response."""
        return InterviewPrepResponse(
            id=prep.id,
            application_id=prep.application_id,
            user_id=prep.user_id,
            interview_date=prep.interview_date,
            notes=prep.notes,
            status=prep.status,
            completed=prep.completed,
            created_at=prep.created_at,
            updated_at=prep.updated_at,
        )
