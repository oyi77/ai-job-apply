"""File upload and management API endpoints."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from typing import Dict, Any, Optional
from pathlib import Path
import uuid
import os

from src.models.user import UserProfile
from src.api.dependencies import get_current_user
from src.utils.logger import get_logger
from src.services.service_registry import service_registry
from src.utils.validators import validate_file_type, validate_file_size

logger = get_logger(__name__)

router = APIRouter()


def create_api_response(data: Any, success: bool = True, message: str = None) -> Dict[str, Any]:
    """Create a standardized API response."""
    response = {"success": success, "data": data}
    if message:
        response["message"] = message
    return response


@router.post("/upload", response_model=Dict[str, Any])
async def upload_file(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Upload a file.
    
    Args:
        file: File to upload
        category: Optional category for the file (e.g., 'resume', 'cover_letter', 'document')
        
    Returns:
        File metadata with ID, filename, and URL
    """
    try:
        logger.info(f"File upload request received: {file.filename}, size: {file.size}, category: {category}")
        
        # Validate file type (allow common document types)
        allowed_extensions = [".pdf", ".docx", ".txt", ".doc", ".rtf", ".odt"]
        if not validate_file_type(file.filename, allowed_extensions):
            logger.warning(f"Invalid file type attempted: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Allowed types: PDF, DOCX, DOC, TXT, RTF, ODT"
            )
        
        # Validate file size (10MB limit)
        if not validate_file_size(file.size, 10.0):
            logger.warning(f"File too large: {file.filename}, size: {file.size}")
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        # Get file service from unified registry
        file_service = await service_registry.get_file_service()
        
        # Read file content
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Determine upload directory based on category
        if category == "resume":
            uploads_dir = Path("backend/uploads/resumes")
        elif category == "cover_letter":
            uploads_dir = Path("backend/uploads/cover_letters")
        else:
            uploads_dir = Path("backend/uploads/files")
        
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file - convert bytes to BytesIO for file service
        from io import BytesIO
        file_content_io = BytesIO(file_content)
        try:
            file_path = await file_service.save_file(file_content_io, unique_filename, str(uploads_dir))
        except Exception as e:
            logger.error(f"Error saving file: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")
        
        # Get file metadata
        file_id = str(uuid.uuid4())
        file_url = f"/api/v1/files/{file_id}/download"
        
        # Store file metadata in database if file repository is available
        try:
            from src.database.repositories.file_repository import FileRepository
            from src.database.config import database_config
            
            async with database_config.get_session() as session:
                file_repo = FileRepository(session)
                file_metadata = await file_repo.create_file_metadata(
                    user_id=current_user.id,
                    filename=file.filename or unique_filename,
                    file_path=str(file_path),
                    file_size=file.size,
                    mime_type=file.content_type or "application/octet-stream",
                    category=category or "general"
                )
                file_id = file_metadata.id
                await session.commit()
        except Exception as e:
            logger.warning(f"Could not store file metadata in database: {e}")
            # Continue without database metadata
        
        logger.info(f"File uploaded successfully: {file.filename} (ID: {file_id})")
        
        return create_api_response(
            {
                "id": file_id,
                "filename": file.filename or unique_filename,
                "url": file_url,
                "size": file.size,
                "category": category or "general"
            },
            True,
            "File uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.get("/{file_id}/download", response_model=Dict[str, Any])
async def download_file(
    file_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Download a file by ID.
    
    Args:
        file_id: File ID
        
    Returns:
        File content
    """
    try:
        # Get file metadata from database
        from src.database.repositories.file_repository import FileRepository
        from src.database.config import database_config
        from fastapi.responses import FileResponse
        
        async with database_config.get_session() as session:
            file_repo = FileRepository(session)
            file_metadata = await file_repo.get_file_metadata(file_id, user_id=current_user.id)
            
            if not file_metadata:
                raise HTTPException(status_code=404, detail="File not found")
            
            file_path = Path(file_metadata.file_path)
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found on disk")
            
            return FileResponse(
                path=str(file_path),
                filename=file_metadata.filename,
                media_type=file_metadata.mime_type
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")


@router.delete("/{file_id}", response_model=Dict[str, Any])
async def delete_file(
    file_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete a file by ID.
    
    Args:
        file_id: File ID
        
    Returns:
        Deletion result
    """
    try:
        # Get file metadata from database
        from src.database.repositories.file_repository import FileRepository
        from src.database.config import database_config
        
        async with database_config.get_session() as session:
            file_repo = FileRepository(session)
            file_metadata = await file_repo.get_file_metadata(file_id, user_id=current_user.id)
            
            if not file_metadata:
                raise HTTPException(status_code=404, detail="File not found")
            
            # Delete file from disk
            file_path = Path(file_metadata.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Delete metadata from database
            await file_repo.delete_file_metadata(file_id)
            await session.commit()
            
            logger.info(f"File deleted successfully: {file_id}")
            
            return create_api_response(
                {"deleted": True},
                True,
                "File deleted successfully"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"File deletion failed: {str(e)}")

