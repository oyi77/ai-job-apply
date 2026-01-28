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
    limit: int = 50, current_user: UserProfile = Depends(get_current_user)
) -> List[AutoApplyActivityLog]:
    """View activity log."""
    service = await service_registry.get_auto_apply_service()
    return await service.get_activity_log(current_user.id, limit=limit)
