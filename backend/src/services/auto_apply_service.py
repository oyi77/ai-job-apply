from typing import List, Optional
from datetime import datetime
import uuid
from typing import TYPE_CHECKING
from src.core.auto_apply_service import AutoApplyService as CoreAutoApplyService
from src.models.automation import (
    AutoApplyConfig,
    AutoApplyConfigCreate,
    AutoApplyActivityLog,
)


class AutoApplyServiceProvider:
    """Provider for AutoApplyService to enable per-user instances."""

    def __init__(self):
        self._service: CoreAutoApplyService = CoreAutoApplyService(None)

    def get_service(self) -> CoreAutoApplyService:
        """Get the AutoApplyService instance."""
        return self._service

    async def initialize(self) -> None:
        """Initialize the service (no-op - creates actual instance per user)."""
        pass

    async def cleanup(self) -> None:
        """Clean up the service."""
        if hasattr(self._service, "cleanup"):
            await self._service.cleanup()


class AutoApplyService:
    def __init__(self, db_session):
        self.db = db_session

    async def create_or_update_config(
        self, user_id: str, config_data: AutoApplyConfigCreate
    ) -> AutoApplyConfig:
        # Implementation to save/update config in DB
        # Mock implementation for now
        return AutoApplyConfig(
            id=str(uuid.uuid4()),
            user_id=user_id,
            is_active=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **config_data.dict(),
        )

    async def get_config(self, user_id: str) -> Optional[AutoApplyConfig]:
        # Implementation to get config from DB
        return None

    async def toggle_auto_apply(self, user_id: str, enabled: bool):
        # Implementation to update is_active status
        pass

    async def get_activity_log(
        self, user_id: str, limit: int = 50
    ) -> List[AutoApplyActivityLog]:
        # Implementation to get activity logs
        return []

    async def run_cycle(self):
        # Implementation for background task
        pass
