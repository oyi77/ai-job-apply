"""Tests for InterviewPrepService."""

import pytest
from datetime import datetime, timedelta
from src.services.interview_prep_service import InterviewPrepServiceImpl
from src.core.interview_service import InterviewPrepCreate, InterviewPrepUpdate


@pytest.fixture
def interview_service():
    """Create an interview prep service instance."""
    return InterviewPrepServiceImpl()


class TestCreatePrep:
    """Test create_prep method."""

    @pytest.mark.asyncio
    async def test_create_prep_success(self, interview_service):
        """Test successful interview prep creation."""
        prep_data = InterviewPrepCreate(
            application_id="app-123",
            interview_date=datetime.utcnow() + timedelta(days=3),
            notes="Prepare for technical round",
        )

        result = await interview_service.create_prep(
            user_id="user-123",
            prep_data=prep_data,
        )

        assert result is not None
        assert result.application_id == "app-123"
        assert result.user_id == "user-123"
        assert result.notes == "Prepare for technical round"
        assert result.status == "scheduled"
        assert result.completed is False
        assert result.id.startswith("prep_")

    @pytest.mark.asyncio
    async def test_create_prep_multiple(self, interview_service):
        """Test creating multiple interview preps."""
        prep1 = InterviewPrepCreate(
            application_id="app-1",
            interview_date=datetime.utcnow() + timedelta(days=1),
        )
        prep2 = InterviewPrepCreate(
            application_id="app-2",
            interview_date=datetime.utcnow() + timedelta(days=2),
        )

        result1 = await interview_service.create_prep("user-1", prep1)
        result2 = await interview_service.create_prep("user-1", prep2)

        assert result1.id != result2.id


class TestGetUpcomingPreps:
    """Test get_upcoming_preps method."""

    @pytest.mark.asyncio
    async def test_get_upcoming_preps(self, interview_service):
        """Test getting upcoming interview preps."""
        # Create preps at different dates
        prep1 = InterviewPrepCreate(
            application_id="app-1",
            interview_date=datetime.utcnow() + timedelta(days=1),
        )
        prep2 = InterviewPrepCreate(
            application_id="app-2",
            interview_date=datetime.utcnow() + timedelta(days=5),
        )
        prep3 = InterviewPrepCreate(
            application_id="app-3",
            interview_date=datetime.utcnow() + timedelta(days=20),  # Too far
        )

        await interview_service.create_prep("user-1", prep1)
        await interview_service.create_prep("user-1", prep2)
        await interview_service.create_prep("user-1", prep3)

        # Get upcoming (7 days)
        upcoming = await interview_service.get_upcoming_preps("user-1", days_ahead=7)

        assert len(upcoming) == 2
        # Should be sorted by date
        assert upcoming[0].application_id == "app-1"
        assert upcoming[1].application_id == "app-2"

    @pytest.mark.asyncio
    async def test_get_upcoming_excludes_completed(self, interview_service):
        """Test that completed preps are excluded."""
        prep = InterviewPrepCreate(
            application_id="app-1",
            interview_date=datetime.utcnow() + timedelta(days=2),
        )
        created = await interview_service.create_prep("user-1", prep)

        # Mark as completed
        await interview_service.update_prep(
            prep_id=created.id,
            user_id="user-1",
            update_data=InterviewPrepUpdate(completed=True),
        )

        upcoming = await interview_service.get_upcoming_preps("user-1")
        assert len(upcoming) == 0


class TestUpdatePrep:
    """Test update_prep method."""

    @pytest.mark.asyncio
    async def test_update_prep_status(self, interview_service):
        """Test updating prep status."""
        prep = InterviewPrepCreate(
            application_id="app-1",
            interview_date=datetime.utcnow() + timedelta(days=3),
        )
        created = await interview_service.create_prep("user-1", prep)

        result = await interview_service.update_prep(
            prep_id=created.id,
            user_id="user-1",
            update_data=InterviewPrepUpdate(status="confirmed", notes="Updated notes"),
        )

        assert result is not None
        assert result.status == "confirmed"
        assert result.notes == "Updated notes"

    @pytest.mark.asyncio
    async def test_update_prep_completed(self, interview_service):
        """Test marking prep as completed."""
        prep = InterviewPrepCreate(
            application_id="app-1",
            interview_date=datetime.utcnow() + timedelta(days=3),
        )
        created = await interview_service.create_prep("user-1", prep)

        result = await interview_service.update_prep(
            prep_id=created.id,
            user_id="user-1",
            update_data=InterviewPrepUpdate(completed=True),
        )

        assert result is not None
        assert result.completed is True
        assert result.status == "completed"


class TestDeletePrep:
    """Test delete_prep method."""

    @pytest.mark.asyncio
    async def test_delete_prep_success(self, interview_service):
        """Test successful prep deletion."""
        prep = InterviewPrepCreate(
            application_id="app-1",
            interview_date=datetime.utcnow() + timedelta(days=3),
        )
        created = await interview_service.create_prep("user-1", prep)

        success = await interview_service.delete_prep(created.id, "user-1")

        assert success is True
        # Verify it's deleted
        fetched = await interview_service.get_prep_by_id(created.id, "user-1")
        assert fetched is None

    @pytest.mark.asyncio
    async def test_delete_prep_wrong_user(self, interview_service):
        """Test that wrong user cannot delete."""
        prep = InterviewPrepCreate(
            application_id="app-1",
            interview_date=datetime.utcnow() + timedelta(days=3),
        )
        created = await interview_service.create_prep("user-1", prep)

        success = await interview_service.delete_prep(created.id, "user-2")

        assert success is False
        # Should still exist
        fetched = await interview_service.get_prep_by_id(created.id, "user-1")
        assert fetched is not None


class TestGetPrepById:
    """Test get_prep_by_id method."""

    @pytest.mark.asyncio
    async def test_get_prep_by_id_success(self, interview_service):
        """Test getting prep by ID."""
        prep = InterviewPrepCreate(
            application_id="app-1",
            interview_date=datetime.utcnow() + timedelta(days=3),
            notes="Test notes",
        )
        created = await interview_service.create_prep("user-1", prep)

        result = await interview_service.get_prep_by_id(created.id, "user-1")

        assert result is not None
        assert result.id == created.id
        assert result.notes == "Test notes"

    @pytest.mark.asyncio
    async def test_get_prep_by_id_not_found(self, interview_service):
        """Test getting non-existent prep."""
        result = await interview_service.get_prep_by_id("nonexistent", "user-1")
        assert result is None
