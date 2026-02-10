"""Account management service interface."""

from abc import ABC, abstractmethod
from typing import Optional
from src.models.user import UserProfile


class AccountService(ABC):
    """Abstract interface for account management services."""

    @abstractmethod
    async def get_account(self, user_id: str) -> Optional[UserProfile]:
        """
        Get account details by user ID.

        Args:
            user_id: User ID

        Returns:
            User profile or None if not found
        """
        pass

    @abstractmethod
    async def delete_account(self, user_id: str, password: str) -> bool:
        """
        Delete a user account and all associated data.

        Args:
            user_id: User ID to delete
            password: User password for confirmation

        Returns:
            True if account deleted successfully
        """
        pass
