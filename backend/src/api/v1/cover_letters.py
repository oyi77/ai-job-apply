"""Cover Letters API endpoints for the AI Job Application Assistant."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from ...models.cover_letter import CoverLetter, CoverLetterCreate, CoverLetterUpdate, BulkDeleteRequest
from ...models.user import UserProfile
from ...api.dependencies import get_current_user
from ...utils.logger import get_logger
from ...services.service_registry import service_registry
from ...utils.response_wrapper import success_response, error_response

logger = get_logger(__name__)

router = APIRouter()


@router.delete("/bulk", response_model=Dict[str, Any])
async def bulk_delete_cover_letters(
    request: BulkDeleteRequest,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Bulk delete cover letters."""
    try:
        cover_letter_service = await service_registry.get_cover_letter_service()
        success = await cover_letter_service.bulk_delete_cover_letters(request.ids, user_id=current_user.id)
        if success:
            return success_response(None, f"Successfully deleted {len(request.ids)} cover letters").dict()
        else:
            return error_response("Some cover letters could not be deleted", status_code=207).dict()
    except Exception as e:
        logger.error(f"Error in bulk deletion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[CoverLetter])
async def get_all_cover_letters(
    current_user: UserProfile = Depends(get_current_user)
) -> List[CoverLetter]:
    """
    Get all cover letters.
    
    Returns:
        List of cover letters
    """
    try:
        # Get cover letter service from unified registry
        cover_letter_service = await service_registry.get_cover_letter_service()
        
        # Get all cover letters
        cover_letters = await cover_letter_service.get_all_cover_letters()
        return cover_letters
        
    except Exception as e:
        logger.error(f"Error getting cover letters: {e}", exc_info=True)
        # Return empty list instead of throwing error for better UX
        return []


@router.get("/{cover_letter_id}", response_model=CoverLetter)
async def get_cover_letter(
    cover_letter_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> CoverLetter:
    """
    Get a specific cover letter by ID.
    
    Args:
        cover_letter_id: Cover letter identifier
        
    Returns:
        Cover letter object
    """
    try:
        # Get cover letter service from unified registry
        cover_letter_service = await service_registry.get_cover_letter_service()
        
        # Get cover letter by ID (filtered by user)
        cover_letter = await cover_letter_service.get_cover_letter(cover_letter_id, user_id=current_user.id)
        
        if not cover_letter:
            raise HTTPException(status_code=404, detail=f"Cover letter {cover_letter_id} not found")
        
        return cover_letter
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cover letter {cover_letter_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get cover letter: {str(e)}")


@router.post("/", response_model=Dict[str, Any])
async def create_cover_letter(
    cover_letter: CoverLetterCreate,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a new cover letter.
    
    Args:
        cover_letter: Cover letter creation data
        
    Returns:
        Consistent API response with created cover letter
    """
    try:
        # Get cover letter service from unified registry
        cover_letter_service = await service_registry.get_cover_letter_service()
        
        # Create cover letter (associated with user)
        created_cover_letter = await cover_letter_service.create_cover_letter(cover_letter, user_id=current_user.id)
        
        logger.info(f"Cover letter created for {created_cover_letter.job_title} at {created_cover_letter.company_name}")
        return success_response(created_cover_letter.dict(), "Cover letter created successfully").dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating cover letter: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create cover letter: {str(e)}")


@router.put("/{cover_letter_id}", response_model=CoverLetter)
async def update_cover_letter(
    cover_letter_id: str,
    cover_letter_update: CoverLetterUpdate,
    current_user: UserProfile = Depends(get_current_user)
) -> CoverLetter:
    """
    Update an existing cover letter.
    
    Args:
        cover_letter_id: Cover letter identifier
        cover_letter_update: Updated cover letter data
        
    Returns:
        Updated cover letter object
    """
    try:
        # Get cover letter service from unified registry
        cover_letter_service = await service_registry.get_cover_letter_service()
        
        # Update cover letter (filtered by user)
        updated_cover_letter = await cover_letter_service.update_cover_letter(cover_letter_id, cover_letter_update, user_id=current_user.id)
        
        if not updated_cover_letter:
            raise HTTPException(status_code=404, detail=f"Cover letter {cover_letter_id} not found")
        
        logger.info(f"Cover letter updated successfully: {cover_letter_id}")
        return updated_cover_letter
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating cover letter {cover_letter_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update cover letter: {str(e)}")


@router.delete("/{cover_letter_id}")
async def delete_cover_letter(
    cover_letter_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete a cover letter.
    
    Args:
        cover_letter_id: Cover letter identifier
        
    Returns:
        Deletion confirmation message
    """
    try:
        # Get cover letter service from unified registry
        cover_letter_service = await service_registry.get_cover_letter_service()
        
        # Delete cover letter (filtered by user)
        success = await cover_letter_service.delete_cover_letter(cover_letter_id, user_id=current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Cover letter {cover_letter_id} not found")
        
        logger.info(f"Cover letter deleted successfully: {cover_letter_id}")
        return {"message": f"Cover letter {cover_letter_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting cover letter {cover_letter_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete cover letter: {str(e)}")


@router.post("/generate", response_model=CoverLetter)
async def generate_cover_letter_with_ai(
    cover_letter_request: CoverLetterCreate,
    current_user: UserProfile = Depends(get_current_user)
) -> CoverLetter:
    """
    Generate a cover letter using AI.
    
    Args:
        cover_letter_request: Cover letter generation request
        
    Returns:
        Generated cover letter object
    """
    try:
        # Get cover letter service from unified registry
        cover_letter_service = await service_registry.get_cover_letter_service()
        
        # Generate cover letter using AI
        generated_cover_letter = await cover_letter_service.generate_cover_letter(cover_letter_request)
        
        logger.info(f"AI-generated cover letter created for {generated_cover_letter.job_title} at {generated_cover_letter.company_name}")
        return generated_cover_letter
        
    except Exception as e:
        logger.error(f"Error generating cover letter with AI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate cover letter: {str(e)}")
