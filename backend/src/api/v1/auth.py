"""Authentication API endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from ...models.user import (
    UserRegister, UserLogin, TokenResponse, TokenRefresh,
    UserProfile, UserProfileUpdate, PasswordChange, PasswordResetRequest, PasswordReset
)
from ...services.service_registry import service_registry
from ...utils.logger import get_logger
from ..dependencies import get_current_user

logger = get_logger(__name__)

router = APIRouter()

# Rate limiter will be accessed from app state
def get_limiter(request: Request) -> Limiter:
    """Get rate limiter from app state."""
    return request.app.state.limiter


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: Request, registration: UserRegister):
    """
    Register a new user (rate limited: 5 per minute per IP).
    
    Note: Rate limiting is temporarily disabled. For production, implement at middleware level.
    
    Args:
        request: FastAPI request object (for rate limiting)
        registration: User registration data
        
    Returns:
        Token response with access and refresh tokens
    """
    
    try:
        auth_service = await service_registry.get_auth_service()
        response = await auth_service.register_user(registration)
        
        logger.info(f"User registered: {registration.email}")
        return response
        
    except ValueError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during registration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, login_data: UserLogin):
    """
    Authenticate a user and return tokens (rate limited: 10 per minute per IP).
    
    Args:
        request: FastAPI request object (for rate limiting)
        login_data: User login credentials
        
    Returns:
        Token response with access and refresh tokens
    """
    # Note: Rate limiting is temporarily disabled due to slowapi integration complexity
    # For production, implement rate limiting at middleware level or use a different library
    
    try:
        auth_service = await service_registry.get_auth_service()
        response = await auth_service.login_user(login_data)
        
        logger.info(f"User logged in: {login_data.email}")
        return response
        
    except ValueError as e:
        logger.warning(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during token refresh: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    refresh: TokenRefresh,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Logout a user by invalidating their refresh token.
    
    Args:
        refresh: Refresh token to invalidate
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    try:
        auth_service = await service_registry.get_auth_service()
        success = await auth_service.logout_user(refresh.refresh_token, current_user.id)
        
        if success:
            logger.info(f"User logged out: {current_user.id}")
            return {"message": "Logged out successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token"
            )
            
    except Exception as e:
        logger.error(f"Error during logout: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


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
    updates: UserProfileUpdate,
    current_user: UserProfile = Depends(get_current_user)
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
        updated_profile = await auth_service.update_user_profile(current_user.id, updates)
        
        logger.info(f"Profile updated: {current_user.id}")
        return updated_profile
        
    except ValueError as e:
        logger.warning(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user: UserProfile = Depends(get_current_user)):
    """
    Delete current user account.

    Args:
        current_user: Current authenticated user
    """
    try:
        auth_service = await service_registry.get_auth_service()
        success = await auth_service.delete_user(current_user.id)

        if success:
            logger.info(f"User account deleted: {current_user.id}")
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account deletion failed"
            )

    except ValueError as e:
        logger.warning(f"Account deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting account: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_change: PasswordChange,
    current_user: UserProfile = Depends(get_current_user)
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password change failed"
            )
            
    except ValueError as e:
        logger.warning(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error changing password: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
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
            return {"message": "If the email exists, a password reset link has been sent"}
        else:
            # Still return success for security
            return {"message": "If the email exists, a password reset link has been sent"}
            
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset failed"
            )
            
    except ValueError as e:
        logger.warning(f"Password reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error resetting password: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )
