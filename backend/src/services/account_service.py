"""Account management service implementation."""

import logging
from typing import Optional
from src.core.account_service import AccountService
from src.core.auth_service import AuthService
from src.models.user import User, UserProfile
from src.database.repositories.user_repository import UserRepository


logger = logging.getLogger(__name__)


class AccountServiceImpl(AccountService):
    """Concrete implementation of AccountService for account management."""

    def __init__(
        self,
        user_repository: UserRepository,
        auth_service: AuthService,
    ):
        """
        Initialize the account service.

        Args:
            user_repository: User repository for data access
            auth_service: Auth service for password verification
        """
        self._repository = user_repository
        self._auth_service = auth_service

    async def get_account(self, user_id: str) -> Optional[UserProfile]:
        """
        Get account details by user ID.

        Args:
            user_id: User ID

        Returns:
            User profile or None if not found
        """
        user = await self._repository.get_by_id(user_id)
        if not user:
            return None

        return UserProfile(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def delete_account(self, user_id: str, password: str) -> bool:
        """
        Delete a user account and all associated data.

        This performs a SOFT delete by marking the user as inactive.
        All associated data (applications, resumes, etc.) is preserved.

        Args:
            user_id: User ID to delete
            password: User password for confirmation

        Returns:
            True if account deleted successfully
            Raises ValueError if user not found or password incorrect
        """
        # Get user
        user = await self._repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Verify password before deletion (security measure)
        if not self._auth_service.verify_password(password, user.password_hash):
            raise ValueError("Password is incorrect")

        # Soft delete - mark user as inactive (preserve data)
        user.is_active = False
        await self._repository.update(user)

        logger.info(f"Account soft-deleted (deactivated) for user: {user_id}")

        return True
