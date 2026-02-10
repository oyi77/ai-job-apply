"""Interview preparation API endpoints."""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.core.interview_service import (
    InterviewPrepCreate,
    InterviewPrepResponse,
    InterviewPrepService,
    InterviewPrepUpdate,
)
from src.core.auth_service import AuthService
from src.models.user import User
from src.database.repositories.user_repository import UserRepository
from src.api.v1.auth import get_current_user


logger = logging.getLogger(__name__)

router = APIRouter()


def get_interview_service() -> InterviewPrepService:
    """
    Get the interview prep service instance.

    In production, this would be managed by ServiceRegistry.
    For now, create a memory-based implementation.
    """
    from src.services.interview_prep_service import InterviewPrepServiceImpl

    return InterviewPrepServiceImpl()


@router.post(
    "/prepare",
    response_model=InterviewPrepResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_interview_prep(
    prep_data: InterviewPrepCreate,
    current_user: User = Depends(get_current_user),
    interview_service: InterviewPrepService = Depends(get_interview_service),
) -> InterviewPrepResponse:
    """
    Create an interview preparation reminder.

    Creates a reminder to prepare for an upcoming interview.
    The reminder will be scheduled based on the interview date.
    """
    try:
        prep = await interview_service.create_prep(
            user_id=current_user.id,
            prep_data=prep_data,
        )
        return prep
    except Exception as e:
        logger.error(f"Error creating interview prep: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create interview preparation",
        )


@router.get("/upcoming", response_model=list[InterviewPrepResponse])
async def get_upcoming_interviews(
    days: int = Query(
        default=7, ge=1, le=30, description="Number of days to look ahead"
    ),
    current_user: User = Depends(get_current_user),
    interview_service: InterviewPrepService = Depends(get_interview_service),
) -> list[InterviewPrepResponse]:
    """
    Get upcoming interview preparations.

    Returns a list of interview preparations within the specified number of days.
    """
    try:
        preps = await interview_service.get_upcoming_preps(
            user_id=current_user.id,
            days_ahead=days,
        )
        return preps
    except Exception as e:
        logger.error(f"Error getting upcoming interviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get upcoming interviews",
        )


@router.get("/{prep_id}", response_model=InterviewPrepResponse)
async def get_interview_prep(
    prep_id: str,
    current_user: User = Depends(get_current_user),
    interview_service: InterviewPrepService = Depends(get_interview_service),
) -> InterviewPrepResponse:
    """
    Get an interview preparation by ID.
    """
    try:
        prep = await interview_service.get_prep_by_id(
            prep_id=prep_id,
            user_id=current_user.id,
        )
        if not prep:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview preparation not found",
            )
        return prep
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interview prep: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get interview preparation",
        )


@router.put("/{prep_id}", response_model=InterviewPrepResponse)
async def update_interview_prep(
    prep_id: str,
    update_data: InterviewPrepUpdate,
    current_user: User = Depends(get_current_user),
    interview_service: InterviewPrepService = Depends(get_interview_service),
) -> InterviewPrepResponse:
    """
    Update an interview preparation.
    """
    try:
        prep = await interview_service.update_prep(
            prep_id=prep_id,
            user_id=current_user.id,
            update_data=update_data,
        )
        if not prep:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview preparation not found",
            )
        return prep
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating interview prep: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update interview preparation",
        )


@router.delete("/{prep_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview_prep(
    prep_id: str,
    current_user: User = Depends(get_current_user),
    interview_service: InterviewPrepService = Depends(get_interview_service),
) -> None:
    """
    Delete an interview preparation.
    """
    try:
        success = await interview_service.delete_prep(
            prep_id=prep_id,
            user_id=current_user.id,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview preparation not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting interview prep: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete interview preparation",
        )
