"""API endpoints for configuration management."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.api.dependencies import get_current_user
from src.models.user import UserProfile
from src.services.config_service import ConfigService
from src.utils.response_wrapper import success_response
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Initialize config service
config_service = ConfigService()


class ConfigCreateRequest(BaseModel):
    """Request model for creating a configuration."""
    name: str = Field(..., description="Configuration name")
    key: str = Field(..., description="Configuration key (unique identifier)")
    value: str = Field(..., description="Configuration value")
    description: Optional[str] = Field(None, description="Configuration description")


class ConfigUpdateRequest(BaseModel):
    """Request model for updating a configuration."""
    value: str = Field(..., description="New configuration value")
    description: Optional[str] = Field(None, description="Updated description")


@router.get("/", response_model=Dict[str, Any])
async def get_all_configs(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get all configurations."""
    try:
        configs = await config_service.get_all_detailed()
        return success_response(configs, "Configurations retrieved successfully").dict()
    except Exception as e:
        logger.error(f"Error getting configs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get configurations: {str(e)}")


@router.get("/{key}", response_model=Dict[str, Any])
async def get_config(
    key: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get a specific configuration by key."""
    try:
        value = await config_service.get(key)
        if value is None:
            raise HTTPException(status_code=404, detail=f"Configuration '{key}' not found")
        
        return success_response(
            {"key": key, "value": value},
            "Configuration retrieved successfully"
        ).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting config {key}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")


@router.post("/", response_model=Dict[str, Any])
async def create_config(
    request: ConfigCreateRequest,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a new configuration."""
    try:
        success = await config_service.set(
            name=request.name,
            key=request.key,
            value=request.value,
            description=request.description
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create configuration")
        
        return success_response(
            {
                "name": request.name,
                "key": request.key,
                "value": request.value,
                "description": request.description
            },
            "Configuration created successfully"
        ).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create configuration: {str(e)}")


@router.put("/{key}", response_model=Dict[str, Any])
async def update_config(
    key: str,
    request: ConfigUpdateRequest,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update a configuration."""
    try:
        # Check if config exists
        existing_value = await config_service.get(key)
        if existing_value is None:
            raise HTTPException(status_code=404, detail=f"Configuration '{key}' not found")
        
        success = await config_service.set(
            name=key.replace("_", " ").title(),  # Generate name from key
            key=key,
            value=request.value,
            description=request.description
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update configuration")
        
        # If this is an AI provider config, reload the config system
        ai_provider_keys = [
            "openai_api_key", "openai_model", "openai_base_url",
            "openrouter_api_key", "openrouter_model", "openrouter_base_url",
            "cursor_api_key", "cursor_model", "cursor_base_url",
            "gemini_api_key", "gemini_model",
            "local_ai_base_url", "local_ai_model"
        ]
        
        if key in ai_provider_keys:
            try:
                from src.config import config
                await config.load_from_database()
                logger.info(f"Reloaded AI provider configs after updating {key}")
            except Exception as e:
                logger.warning(f"Could not reload configs: {e}")
        
        return success_response(
            {"key": key, "value": request.value, "description": request.description},
            "Configuration updated successfully"
        ).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating config {key}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


@router.delete("/{key}", response_model=Dict[str, Any])
async def delete_config(
    key: str,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a configuration."""
    try:
        success = await config_service.delete(key)
        if not success:
            raise HTTPException(status_code=404, detail=f"Configuration '{key}' not found")
        
        return success_response(
            {"key": key},
            "Configuration deleted successfully"
        ).dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting config {key}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete configuration: {str(e)}")


@router.get("/ai-providers/list", response_model=Dict[str, Any])
async def get_ai_provider_configs(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get AI provider configurations."""
    try:
        providers = await config_service.get_ai_provider_configs()
        return success_response(
            providers,
            "AI provider configurations retrieved successfully"
        ).dict()
    except Exception as e:
        logger.error(f"Error getting AI provider configs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get AI provider configurations: {str(e)}")

