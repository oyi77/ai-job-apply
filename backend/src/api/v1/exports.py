"""Export API endpoints for generating reports in various formats."""

import io
from fastapi import APIRouter, HTTPException, Depends, Response, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from ...models.user import UserProfile
from ...services.service_registry import service_registry
from ...utils.response_wrapper import success_response, error_response
from ..dependencies import get_current_user
from pydantic import BaseModel, Field


router = APIRouter()


class ExportRequest(BaseModel):
    """Export request model."""
    format: str = Field(default="csv", description="Export format (pdf, csv, excel)")
    application_ids: Optional[List[str]] = Field(None, description="Specific application IDs to export. If None, all will be exported.")
    date_from: Optional[datetime] = Field(None, description="Start date for filtering")
    date_to: Optional[datetime] = Field(None, description="End date for filtering")


class AnalyticsExportRequest(BaseModel):
    """Analytics export request model."""
    format: str = Field(default="pdf", description="Export format (pdf, csv, excel)")
    include_charts: bool = Field(default=True, description="Include charts in export")


@router.post("/applications")
async def export_applications(
    request: ExportRequest,
    current_user: UserProfile = Depends(get_current_user)
) -> Response:
    """
    Export job applications in the specified format.
    
    Args:
        request: Export request with format and filters
        current_user: Current authenticated user
        
    Returns:
        File download response
    """
    try:
        # Get application service
        application_service = await service_registry.get_application_service()
        
        # Get applications
        if request.application_ids:
            applications = []
            for app_id in request.application_ids:
                app = await application_service.get_application(app_id)
                if app:
                    applications.append(app)
        else:
            all_apps = await application_service.get_all_applications()
            applications = all_apps
        
        # Filter by date if provided
        if request.date_from or request.date_to:
            filtered_apps = []
            for app in applications:
                app_date = app.applied_date or app.created_at
                if app_date:
                    if request.date_from and app_date < request.date_from:
                        continue
                    if request.date_to and app_date > request.date_to:
                        continue
                filtered_apps.append(app)
            applications = filtered_apps
        
        if not applications:
            raise HTTPException(status_code=404, detail="No applications found to export")
        
        # Convert to dictionaries
        apps_dict = [app.dict() if hasattr(app, 'dict') else app for app in applications]
        
        # Get export service
        export_service = await service_registry.get_export_service()
        
        # Generate export
        file_data = await export_service.export_applications(
            apps_dict,
            format=request.format,
            user_id=current_user.id
        )
        
        # Determine content type and file extension
        content_type_map = {
            "pdf": "application/pdf",
            "csv": "text/csv",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        
        extension_map = {
            "pdf": "pdf",
            "csv": "csv",
            "excel": "xlsx",
            "xlsx": "xlsx"
        }
        
        format_lower = request.format.lower()
        content_type = content_type_map.get(format_lower, "application/octet-stream")
        extension = extension_map.get(format_lower, "bin")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"applications_export_{timestamp}.{extension}"
        
        logger.info(f"Exported {len(applications)} applications to {format_lower} for user {current_user.id}")
        
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except ValueError as e:
        logger.error(f"Export validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting applications: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to export applications: {str(e)}")


@router.post("/resumes")
async def export_resumes(
    format: str = Query(default="csv", description="Export format (pdf, csv, excel)"),
    current_user: UserProfile = Depends(get_current_user)
) -> Response:
    """
    Export resumes in the specified format.
    
    Args:
        format: Export format
        current_user: Current authenticated user
        
    Returns:
        File download response
    """
    try:
        # Get resume service
        resume_service = await service_registry.get_resume_service()
        
        # Get all resumes
        resumes = await resume_service.get_all_resumes()
        
        if not resumes:
            raise HTTPException(status_code=404, detail="No resumes found to export")
        
        # Convert to dictionaries
        resumes_dict = [resume.dict() if hasattr(resume, 'dict') else resume for resume in resumes]
        
        # Get export service
        export_service = await service_registry.get_export_service()
        
        # Generate export
        file_data = await export_service.export_resumes(
            resumes_dict,
            format=format,
            user_id=current_user.id
        )
        
        # Determine content type and file extension
        content_type_map = {
            "pdf": "application/pdf",
            "csv": "text/csv",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        
        extension_map = {
            "pdf": "pdf",
            "csv": "csv",
            "excel": "xlsx",
            "xlsx": "xlsx"
        }
        
        format_lower = format.lower()
        content_type = content_type_map.get(format_lower, "application/octet-stream")
        extension = extension_map.get(format_lower, "bin")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resumes_export_{timestamp}.{extension}"
        
        logger.info(f"Exported {len(resumes)} resumes to {format_lower} for user {current_user.id}")
        
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except ValueError as e:
        logger.error(f"Export validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting resumes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to export resumes: {str(e)}")


@router.post("/cover-letters")
async def export_cover_letters(
    format: str = Query(default="pdf", description="Export format (pdf, csv, excel)"),
    current_user: UserProfile = Depends(get_current_user)
) -> Response:
    """
    Export cover letters in the specified format.
    
    Args:
        format: Export format
        current_user: Current authenticated user
        
    Returns:
        File download response
    """
    try:
        # Get cover letter service
        cover_letter_service = await service_registry.get_cover_letter_service()
        
        # Get all cover letters
        cover_letters = await cover_letter_service.get_all_cover_letters()
        
        if not cover_letters:
            raise HTTPException(status_code=404, detail="No cover letters found to export")
        
        # Convert to dictionaries
        cls_dict = [cl.dict() if hasattr(cl, 'dict') else cl for cl in cover_letters]
        
        # Get export service
        export_service = await service_registry.get_export_service()
        
        # Generate export
        file_data = await export_service.export_cover_letters(
            cls_dict,
            format=format,
            user_id=current_user.id
        )
        
        # Determine content type and file extension
        content_type_map = {
            "pdf": "application/pdf",
            "csv": "text/csv",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        
        extension_map = {
            "pdf": "pdf",
            "csv": "csv",
            "excel": "xlsx",
            "xlsx": "xlsx"
        }
        
        format_lower = format.lower()
        content_type = content_type_map.get(format_lower, "application/octet-stream")
        extension = extension_map.get(format_lower, "bin")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cover_letters_export_{timestamp}.{extension}"
        
        logger.info(f"Exported {len(cover_letters)} cover letters to {format_lower} for user {current_user.id}")
        
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except ValueError as e:
        logger.error(f"Export validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting cover letters: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to export cover letters: {str(e)}")


@router.post("/analytics")
async def export_analytics(
    request: AnalyticsExportRequest,
    current_user: UserProfile = Depends(get_current_user)
) -> Response:
    """
    Export analytics data in the specified format.
    
    Args:
        request: Analytics export request
        current_user: Current authenticated user
        
    Returns:
        File download response
    """
    try:
        # Get application service for statistics
        application_service = await service_registry.get_application_service()
        
        # Get analytics data
        stats = await application_service.get_application_stats()
        
        # Build analytics data dictionary
        analytics_data = {
            "statistics": stats,
            "generated_at": datetime.now().isoformat(),
            "user_id": current_user.id
        }
        
        # Get export service
        export_service = await service_registry.get_export_service()
        
        # Generate export
        file_data = await export_service.export_analytics(
            analytics_data,
            format=request.format,
            user_id=current_user.id
        )
        
        # Determine content type and file extension
        content_type_map = {
            "pdf": "application/pdf",
            "csv": "text/csv",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        
        extension_map = {
            "pdf": "pdf",
            "csv": "csv",
            "excel": "xlsx",
            "xlsx": "xlsx"
        }
        
        format_lower = request.format.lower()
        content_type = content_type_map.get(format_lower, "application/octet-stream")
        extension = extension_map.get(format_lower, "bin")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analytics_export_{timestamp}.{extension}"
        
        logger.info(f"Exported analytics to {format_lower} for user {current_user.id}")
        
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except ValueError as e:
        logger.error(f"Export validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to export analytics: {str(e)}")


@router.get("/formats")
async def get_export_formats(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get list of supported export formats.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of supported formats
    """
    try:
        export_service = await service_registry.get_export_service()
        formats = await export_service.get_supported_formats()
        
        return success_response(
            {"formats": formats},
            "Supported export formats retrieved successfully"
        ).dict()
        
    except Exception as e:
        logger.error(f"Error getting export formats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get export formats: {str(e)}")
