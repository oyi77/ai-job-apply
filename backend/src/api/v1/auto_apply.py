from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from src.models.user import UserProfile
from src.api.dependencies import get_current_user
from src.services.service_registry import service_registry
from src.models.automation import (
    AutoApplyConfig,
    AutoApplyConfigCreate,
    AutoApplyConfigUpdate,
    AutoApplyActivityLog,
)

router = APIRouter()


@router.post("/config", response_model=AutoApplyConfig)
async def create_update_config(
    config_data: AutoApplyConfigCreate,
    current_user: UserProfile = Depends(get_current_user),
) -> AutoApplyConfig:
    """Create or update auto-apply configuration."""
    service = await service_registry.get_auto_apply_service()
    return await service.create_or_update_config(current_user.id, config_data)


@router.get("/config", response_model=Optional[AutoApplyConfig])
async def get_config(
    current_user: UserProfile = Depends(get_current_user),
) -> Optional[AutoApplyConfig]:
    """Get auto-apply configuration."""
    service = await service_registry.get_auto_apply_service()
    return await service.get_config(current_user.id)


@router.post("/start", response_model=Dict[str, str])
async def start_auto_apply(
    current_user: UserProfile = Depends(get_current_user),
) -> Dict[str, str]:
    """Activate auto-apply."""
    service = await service_registry.get_auto_apply_service()
    await service.toggle_auto_apply(current_user.id, enabled=True)
    return {"message": "Auto-apply started"}


@router.post("/stop", response_model=Dict[str, str])
async def stop_auto_apply(
    current_user: UserProfile = Depends(get_current_user),
) -> Dict[str, str]:
    """Deactivate auto-apply."""
    service = await service_registry.get_auto_apply_service()
    await service.toggle_auto_apply(current_user.id, enabled=False)
    return {"message": "Auto-apply stopped"}


@router.get("/activity", response_model=List[AutoApplyActivityLog])
async def get_activity_log(
    limit: int = 50,
    offset: int = 0,
    current_user: UserProfile = Depends(get_current_user),
) -> List[AutoApplyActivityLog]:
    """View activity log with pagination."""
    service = await service_registry.get_auto_apply_service()
    return await service.get_activity_log(current_user.id, limit=limit, offset=offset)


@router.post("/rate-limits", response_model=Dict[str, str])
async def update_rate_limits(
    platform: str,
    hourly_limit: Optional[int] = None,
    daily_limit: Optional[int] = None,
    current_user: UserProfile = Depends(get_current_user),
) -> Dict[str, str]:
    """Update rate limits for a platform."""
    service = await service_registry.get_auto_apply_service()
    await service.update_rate_limits(
        current_user.id,
        platform=platform,
        hourly_limit=hourly_limit,
        daily_limit=daily_limit,
    )
    return {"message": f"Rate limits updated for {platform}"}


@router.get("/queue", response_model=List[Dict[str, Any]])
async def get_external_site_queue(
    limit: int = 20, current_user: UserProfile = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get queued external site applications for manual review."""
    service = await service_registry.get_auto_apply_service()
    return await service.get_external_site_queue(current_user.id, limit=limit)


@router.post("/retry-queued", response_model=Dict[str, str])
async def retry_queued_application(
    job_id: str, current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, str]:
    """Retry a queued external site application."""
    service = await service_registry.get_auto_apply_service()
    await service.retry_queued_application(current_user.id, job_id)
    return {"message": f"Application {job_id} queued for retry"}


@router.post("/skip-queued", response_model=Dict[str, str])
async def skip_queued_application(
    job_id: str, reason: str, current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, str]:
    """Skip a queued external site application."""
    service = await service_registry.get_auto_apply_service()
    await service.skip_queued_application(current_user.id, job_id, reason)
    return {"message": f"Application {job_id} skipped: {reason}"}
