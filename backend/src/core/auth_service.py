"""Authentication service interface."""

from abc import ABC, abstractmethod
from typing import Optional
from src.models.user import (
    User,
    UserRegister,
    UserLogin,
    TokenResponse,
    UserProfile,
    UserProfileUpdate,
    PasswordChange,
    PasswordResetRequest,
    PasswordReset,
)


class AuthService(ABC):
    """Abstract base class for authentication services."""

    @abstractmethod
    async def register_user(self, registration: UserRegister) -> TokenResponse:
        """
        Register a new user.

        Args:
            registration: User registration data

        Returns:
            Token response with access and refresh tokens

        Raises:
            ValueError: If email already exists or validation fails
        """
        pass

    @abstractmethod
    async def login_user(self, login: UserLogin) -> TokenResponse:
        """
        Authenticate a user and return tokens.

        Args:
            login: User login credentials

        Returns:
            Token response with access and refresh tokens

        Raises:
            ValueError: If credentials are invalid
        """
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh an access token using a refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New token response with access and refresh tokens

        Raises:
            ValueError: If refresh token is invalid or expired
        """
        pass

    @abstractmethod
    async def logout_user(self, refresh_token: str, user_id: str) -> bool:
        """
        Logout a user by invalidating their refresh token.

        Args:
            refresh_token: Refresh token to invalidate
            user_id: User ID

        Returns:
            True if logout successful
        """
        pass

    @abstractmethod
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile by ID.

        Args:
            user_id: User ID

        Returns:
            User profile or None if not found
        """
        pass

    @abstractmethod
    async def update_user_profile(
        self, user_id: str, updates: UserProfileUpdate
    ) -> UserProfile:
        """
        Update user profile.

        Args:
            user_id: User ID
            updates: Profile update data

        Returns:
            Updated user profile

        Raises:
            ValueError: If user not found or validation fails
        """
        pass

    @abstractmethod
    async def change_password(
        self, user_id: str, password_change: PasswordChange
    ) -> bool:
        """
        Change user password.

        Args:
            user_id: User ID
            password_change: Password change data

        Returns:
            True if password changed successfully

        Raises:
            ValueError: If current password is incorrect or validation fails
        """
        pass

    @abstractmethod
    async def verify_token(self, token: str) -> Optional[str]:
        """
        Verify JWT token and return user ID.

        Args:
            token: JWT access token

        Returns:
            User ID if token is valid, None otherwise
        """
        pass

    @abstractmethod
    async def delete_user(self, user_id: str, password: str) -> bool:
        """
        Delete user account and all associated data.

        Args:
            user_id: User ID to delete
            password: User password for confirmation

        Returns:
            True if account deleted successfully
        """
        pass

    @abstractmethod
    async def request_password_reset(self, reset_request: PasswordResetRequest) -> bool:
        """
        Request a password reset by generating a reset token.

        Args:
            reset_request: Password reset request with email

        Returns:
            True if reset token generated (always returns True for security)

        Raises:
            ValueError: If email not found (but still returns True for security)
        """
        pass

    @abstractmethod
    async def reset_password(self, reset: PasswordReset) -> bool:
        """
        Reset password using a reset token.

        Args:
            reset: Password reset data with token and new password

        Returns:
            True if password reset successful

        Raises:
            ValueError: If token is invalid or expired
        """
        pass

    @abstractmethod
    async def delete_user(self, user_id: str, password: str) -> bool:
        """
        Delete a user account and all associated data.

        Args:
            user_id: User ID to delete
            password: User password for confirmation

        Returns:
            True if account deleted successfully

        Raises:
            ValueError: If password is incorrect or user not found
        """
        pass
