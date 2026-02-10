"""Authentication API endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status, Request, Body
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.config import config
from src.models.user import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    UserProfile,
    UserProfileUpdate,
    PasswordChange,
    PasswordResetRequest,
    PasswordReset,
)
from pydantic import BaseModel
from src.services.service_registry import service_registry
from src.utils.logger import get_logger
from src.api.dependencies import get_current_user

logger = get_logger(__name__)

router = APIRouter()


# Rate limiter will be accessed from app state
def get_limiter(request: Request) -> Limiter:
    """Get rate limiter from app state."""
    return request.app.state.limiter


# Create rate limiter instance for this router (shares storage with app's limiter)
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit(
    f"{config.rate_limit_auth_per_minute}/minute"
    if config.rate_limit_enabled
    else "1000/minute"
)
async def register(request: Request, registration: UserRegister):
    """
    Register a new user (rate limited: 5 per minute per IP).

    Args:
        request: FastAPI request object (for rate limiting)
        registration: User registration data

    Returns:
        Token response with access and refresh tokens
    """

    try:
        auth_service = await service_registry.get_auth_service()
        logger.info(
            f"Attempting to register user: {registration.email}, name: {registration.name}"
        )
        logger.debug(f"Registration data: {registration.model_dump()}")

        response = await auth_service.register_user(registration)

        logger.info(f"User registered successfully: {registration.email}")
        logger.debug(f"Token response: {response.model_dump()}")
        return response

    except ValueError as e:
        logger.warning(f"Registration failed - ValueError: {e}", exc_info=True)
        logger.debug(
            f"Validation error details: {type(e).__name__}: {e}", exc_info=True
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(
            f"Error during registration: {type(e).__name__}: {e}", exc_info=True
        )
        logger.debug(f"Full error traceback:", exc_info=True)
        import traceback

        logger.debug(traceback.format_exc(), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )
        logger.debug(f"Registration data: {registration.model_dump()}")

        response = await auth_service.register_user(registration)

        logger.info(f"User registered successfully: {registration.email}")
        logger.debug(f"Token response: {response.model_dump()}")
        return response

    except ValueError as e:
        logger.warning(f"Registration failed - ValueError: {e}", exc_info=True)
        logger.debug(f"Validation error details: {type(e).__name__}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(
            f"Error during registration: {type(e).__name__}: {e}", exc_info=True
        )
        logger.debug(f"Error traceback", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=TokenResponse)
@limiter.limit(
    f"{config.rate_limit_auth_per_minute}/minute"
    if config.rate_limit_enabled
    else "1000/minute"
)
async def login(request: Request, login_data: UserLogin):
    """
    Authenticate a user and return tokens (rate limited: 10 per minute per IP).

    Args:
        request: FastAPI request object (for rate limiting)
        login_data: User login credentials

    Returns:
        Token response with access and refresh tokens
    """
    try:
        auth_service = await service_registry.get_auth_service()
        response = await auth_service.login_user(login_data)

        logger.info(f"User logged in: {login_data.email}")
        return response

    except ValueError as e:
        logger.warning(f"Login failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Error during login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh: TokenRefresh):
    """
    Refresh an access token using a refresh token.

    Args:
        refresh: Refresh token data

    Returns:
        New token response with access and refresh tokens
    """
    try:
        auth_service = await service_registry.get_auth_service()
        response = await auth_service.refresh_token(refresh.refresh_token)

        logger.debug("Token refreshed successfully")
        return response

    except ValueError as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Error during token refresh: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(refresh: TokenRefresh):
    """
    Logout a user by invalidating their refresh token.

    This endpoint does NOT require authentication to allow logout even with expired tokens.
    This prevents users from being stuck in a stale state where they can't logout.

    Args:
        refresh: Refresh token to invalidate

    Returns:
        Success message (always succeeds to allow frontend cleanup even if token is invalid)
    """
    try:
        auth_service = await service_registry.get_auth_service()
        # Try to get user_id from refresh token if possible (optional)
        user_id = None
        try:
            user_id = await auth_service.verify_refresh_token(refresh.refresh_token)
        except Exception:
            # If refresh token is invalid/expired, that's ok - we'll still try to invalidate it
            pass

        # Attempt to invalidate the refresh token
        # This will succeed even if the token is already invalid (idempotent operation)
        success = await auth_service.logout_user(refresh.refresh_token, user_id)

        if success or user_id is None:
            # Successfully logged out, or token was already invalid (allow logout anyway)
            if user_id:
                logger.info(f"User logged out: {user_id}")
            else:
                logger.debug(
                    "Logout called with invalid/expired token (allowing cleanup)"
                )
            return {"message": "Logged out successfully"}
        else:
            # Even if logout_user returns False, we still return success
            # This prevents users from being stuck if there's any issue invalidating the token
            logger.warning(
                "Logout called but token invalidation returned False (allowing anyway)"
            )
            return {"message": "Logged out successfully"}

    except Exception as e:
        logger.error(f"Error during logout: {e}", exc_info=True)
        # Even on error, return success to allow frontend to clear tokens
        # This prevents users from being stuck with stale tokens
        return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: UserProfile = Depends(get_current_user)):
    """
    Get current user profile.

    Args:
        current_user: Current authenticated user

    Returns:
        User profile
    """
    return current_user


@router.put("/me", response_model=UserProfile)
async def update_profile(
    updates: UserProfileUpdate, current_user: UserProfile = Depends(get_current_user)
):
    """
    Update current user profile.

    Args:
        updates: Profile update data
        current_user: Current authenticated user

    Returns:
        Updated user profile
    """
    try:
        auth_service = await service_registry.get_auth_service()
        updated_profile = await auth_service.update_user_profile(
            current_user.id, updates
        )

        logger.info(f"Profile updated: {current_user.id}")
        return updated_profile

    except ValueError as e:
        logger.warning(f"Profile update failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed",
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    password_data: dict = Body(...),
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Delete current user account.

    Requires password confirmation for security.

    Args:
        password_data: Request body containing password confirmation
        current_user: Current authenticated user

    Request body (JSON):
        {
            "password": "user_current_password"
        }
    """
    password = password_data.get("password")
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password confirmation required",
        )

    try:
        auth_service = await service_registry.get_auth_service()
        success = await auth_service.delete_user(current_user.id, password)

        if success:
            logger.info(f"User account deleted: {current_user.id}")
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account deletion failed",
            )

    except ValueError as e:
        logger.warning(f"Account deletion failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting account: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed",
        )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_change: PasswordChange,
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Change user password.

    Args:
        password_change: Password change data
        current_user: Current authenticated user

    Returns:
        Success message
    """
    try:
        auth_service = await service_registry.get_auth_service()
        success = await auth_service.change_password(current_user.id, password_change)

        if success:
            logger.info(f"Password changed: {current_user.id}")
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password change failed"
            )

    except ValueError as e:
        logger.warning(f"Password change failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error changing password: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed",
        )


@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(reset_request: PasswordResetRequest):
    """
    Request a password reset.

    Args:
        reset_request: Password reset request with email

    Returns:
        Success message (always returns success for security)
    """
    try:
        auth_service = await service_registry.get_auth_service()
        success = await auth_service.request_password_reset(reset_request)

        if success:
            logger.info(f"Password reset requested for: {reset_request.email}")
            # Always return success to prevent email enumeration
            return {
                "message": "If the email exists, a password reset link has been sent"
            }
        else:
            # Still return success for security
            return {
                "message": "If the email exists, a password reset link has been sent"
            }

    except Exception as e:
        logger.error(f"Error requesting password reset: {e}", exc_info=True)
        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(reset: PasswordReset):
    """
    Reset password using a reset token.

    Args:
        reset: Password reset data with token and new password

    Returns:
        Success message
    """
    try:
        auth_service = await service_registry.get_auth_service()
        success = await auth_service.reset_password(reset)

        if success:
            logger.info("Password reset successful")
            return {"message": "Password reset successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password reset failed"
            )

    except ValueError as e:
        logger.warning(f"Password reset failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error resetting password: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed",
        )


class AccountDeletionRequest(BaseModel):
    """Request model for account deletion."""

    password: str


@router.delete("/account", status_code=status.HTTP_200_OK)
async def delete_account(
    password: str = Body(..., embed=True),
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Delete user account and all associated data.

    This is a destructive operation that cannot be undone.
    All user data (applications, resumes, cover letters) will be permanently deleted.

    Args:
        password: User password for confirmation
        current_user: Current authenticated user

    Returns:
        Success message
    """
    try:
        auth_service = await service_registry.get_auth_service()
        success = await auth_service.delete_user(current_user.id, password)

        if success:
            logger.info(f"Account deleted: {current_user.id}")
            return {"message": "Account deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account deletion failed",
            )

    except ValueError as e:
        logger.warning(f"Account deletion failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting account: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed",
        )
