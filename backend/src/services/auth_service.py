"""JWT-based authentication service implementation."""

from datetime import datetime, timezone, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import bcrypt

from src.core.auth_service import AuthService
from src.models.user import (
    User, UserRegister, UserLogin, TokenResponse, UserProfile, 
    UserProfileUpdate, PasswordChange, PasswordResetRequest, PasswordReset
)
from src.services.email_service import EmailService
from src.database.repositories.user_repository import UserRepository
from src.database.config import database_config
from src.config import config
from src.utils.logger import get_logger
import uuid


class JWTAuthService(AuthService):
    """JWT-based authentication service."""
    
    def __init__(self, email_service: Optional[EmailService] = None):
        """Initialize JWT auth service."""
        self.logger = get_logger(__name__)
        self._repository_class = UserRepository
        self.email_service = email_service
    
    async def initialize(self) -> None:
        """Initialize the service."""
        self.logger.info("JWT Auth Service initialized")
    
    async def cleanup(self) -> None:
        """Cleanup service resources."""
        pass

    @asynccontextmanager
    async def _get_session_repo(self):
        """Context manager for session and repository."""
        async with database_config.get_session() as session:
            yield session, self._repository_class(session)
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against a hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    
    def _create_access_token(self, user_id: str, email: str) -> str:
        """Create a JWT access token."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=config.jwt_access_token_expire_minutes)
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(
            payload,
            config.jwt_secret_key,
            algorithm=config.jwt_algorithm
        )
    
    def _create_refresh_token(self, user_id: str) -> str:
        """Create a JWT refresh token."""
        expire = datetime.now(timezone.utc) + timedelta(days=config.jwt_refresh_token_expire_days)
        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh",
            "jti": str(uuid.uuid4())
        }
        return jwt.encode(
            payload,
            config.jwt_secret_key,
            algorithm=config.jwt_algorithm
        )
    
    async def register_user(self, registration: UserRegister) -> TokenResponse:
        """Register a new user."""
        async with self._get_session_repo() as (session, repository):
            # Check if user already exists
            existing_user = await repository.get_by_email(registration.email)
            if existing_user:
                raise ValueError("Email already registered")
            
            # Create new user
            user = User(
                id=str(uuid.uuid4()),
                email=registration.email.lower(),
                password_hash=self._hash_password(registration.password),
                name=registration.name,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Save user
            created_user = await repository.create(user)
            
            # Create tokens
            access_token = self._create_access_token(created_user.id, created_user.email)
            refresh_token = self._create_refresh_token(created_user.id)
            
            # Create session
            expires_at = datetime.now(timezone.utc) + timedelta(days=config.jwt_refresh_token_expire_days)
            await repository.create_session(created_user.id, refresh_token, expires_at)
        
        self.logger.info(f"User registered: {created_user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=config.jwt_access_token_expire_minutes * 60
        )
    
    async def login_user(self, login: UserLogin) -> TokenResponse:
        """Authenticate a user and return tokens."""
        async with self._get_session_repo() as (session, repository):
            # Normalize email (lowercase) for consistent lookup
            email = login.email.lower() if login.email else ""
            # Get user by email
            user = await repository.get_by_email(email)
            if not user:
                # Don't reveal if email exists
                raise ValueError("Invalid email or password")
            
            # Check if account is locked
            if config.account_lockout_enabled and user.account_locked_until:
                if user.account_locked_until > datetime.now(timezone.utc):
                    remaining_minutes = int((user.account_locked_until - datetime.now(timezone.utc)).total_seconds() / 60)
                    raise ValueError(f"Account is locked. Please try again in {remaining_minutes} minutes.")
                else:
                    # Lockout expired, reset failed attempts
                    await repository.reset_failed_login_attempts(user.id)
                    user = await repository.get_by_id(user.id)  # Refresh user data
            
            # Check if user is active
            if not user.is_active:
                raise ValueError("Account is disabled")
            
            # Verify password
            password_valid = self._verify_password(login.password, user.password_hash)
            
            if not password_valid:
                # Increment failed login attempts
                if config.account_lockout_enabled:
                    failed_attempts = await repository.increment_failed_login_attempts(user.id)
                    if failed_attempts >= config.max_failed_login_attempts:
                        lockout_until = datetime.now(timezone.utc) + timedelta(minutes=config.account_lockout_duration_minutes)
                        await repository.lock_account(user.id, lockout_until)
                        self.logger.warning(f"Account locked due to {failed_attempts} failed login attempts: {user.email}")
                        raise ValueError(f"Too many failed login attempts. Account locked for {config.account_lockout_duration_minutes} minutes.")
                raise ValueError("Invalid email or password")
            
            # Successful login - reset failed attempts
            if config.account_lockout_enabled and user.failed_login_attempts > 0:
                await repository.reset_failed_login_attempts(user.id)
            
            # Create tokens
            access_token = self._create_access_token(user.id, user.email)
            refresh_token = self._create_refresh_token(user.id)
            
            # Create session
            expires_at = datetime.now(timezone.utc) + timedelta(days=config.jwt_refresh_token_expire_days)
            await repository.create_session(user.id, refresh_token, expires_at)
        
        self.logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=config.jwt_access_token_expire_minutes * 60
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh an access token using a refresh token."""
        async with self._get_session_repo() as (session, repository):
            try:
                # Verify refresh token
                payload = jwt.decode(
                    refresh_token,
                    config.jwt_secret_key,
                    algorithms=[config.jwt_algorithm]
                )
                
                if payload.get("type") != "refresh":
                    raise ValueError("Invalid token type")
                
                user_id = payload.get("sub")
                if not user_id:
                    raise ValueError("Invalid token")
                
                # Verify session exists and is active
                session_obj = await repository.get_session(refresh_token)
                if not session_obj or session_obj.user_id != user_id:
                    raise ValueError("Invalid or expired refresh token")
                
                # Get user
                user = await repository.get_by_id(user_id)
                if not user or not user.is_active:
                    raise ValueError("User not found or inactive")
                
                # Invalidate old session
                await repository.invalidate_session(refresh_token)
                
                # Create new tokens
                access_token = self._create_access_token(user.id, user.email)
                new_refresh_token = self._create_refresh_token(user.id)
                
                # Create new session
                expires_at = datetime.now(timezone.utc) + timedelta(days=config.jwt_refresh_token_expire_days)
                await repository.create_session(user.id, new_refresh_token, expires_at)
                
                return TokenResponse(
                    access_token=access_token,
                    refresh_token=new_refresh_token,
                    token_type="bearer",
                    expires_in=config.jwt_access_token_expire_minutes * 60
                )
            
            except JWTError as e:
                self.logger.warning(f"JWT error during token refresh: {e}")
                raise ValueError("Invalid or expired refresh token")
    
    async def logout_user(self, refresh_token: str, user_id: Optional[str] = None) -> bool:
        """Logout a user by invalidating their refresh token.
        
        Args:
            refresh_token: Refresh token to invalidate
            user_id: Optional user ID (if None, will try to extract from token)
            
        Returns:
            True if token was invalidated, False otherwise
        """
        async with self._get_session_repo() as (session, repository):
            # Try to get user_id from token if not provided
            if user_id is None:
                try:
                    payload = jwt.decode(
                        refresh_token,
                        config.jwt_secret_key,
                        algorithms=[config.jwt_algorithm]
                    )
                    if payload.get("type") == "refresh":
                        user_id = payload.get("sub")
                except JWTError:
                    # Token is invalid/expired, that's ok - we'll still try to invalidate it
                    user_id = None
            
            # Try to get session by refresh token
            session_obj = await repository.get_session(refresh_token)
            if session_obj:
                # If we have user_id, verify it matches
                if user_id and session_obj.user_id != user_id:
                    self.logger.warning(f"Refresh token user_id mismatch during logout")
                    return False
                
                # Invalidate the session
                await repository.invalidate_session(refresh_token)
                self.logger.info(f"User logged out: {session_obj.user_id or user_id or 'unknown'}")
                return True
            elif user_id:
                # Token not in database but we have user_id - try to invalidate all user sessions
                await repository.invalidate_all_user_sessions(user_id)
                self.logger.info(f"Invalidated all sessions for user: {user_id}")
                return True
        
        # Token not found and no user_id - token may already be invalid
        # Return True anyway to allow frontend cleanup (even if token is invalid)
        self.logger.debug("Logout called with invalid token, returning True for frontend cleanup")
        return True
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID."""
        async with self._get_session_repo() as (session, repository):
            user = await repository.get_by_id(user_id)
            if not user:
                return None
            
            return UserProfile(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
    
    async def update_user_profile(self, user_id: str, updates: UserProfileUpdate) -> UserProfile:
        """Update user profile."""
        async with self._get_session_repo() as (session, repository):
            # Check if email is being updated and if it's already taken
            if updates.email:
                existing_user = await repository.get_by_email(updates.email)
                if existing_user and existing_user.id != user_id:
                    raise ValueError("Email already in use")
            
            # Update user
            updated_user = await repository.update(user_id, updates)
            if not updated_user:
                raise ValueError("User not found")
            
            self.logger.info(f"User profile updated: {user_id}")
            
            return UserProfile(
                id=updated_user.id,
                email=updated_user.email,
                name=updated_user.name,
                created_at=updated_user.created_at,
                updated_at=updated_user.updated_at
            )
    
    async def change_password(self, user_id: str, password_change: PasswordChange) -> bool:
        """Change user password."""
        async with self._get_session_repo() as (session, repository):
            # Get user
            user = await repository.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Verify current password
            if not self._verify_password(password_change.current_password, user.password_hash):
                raise ValueError("Current password is incorrect")
            
            # Hash new password
            new_password_hash = self._hash_password(password_change.new_password)
            
            # Update password
            success = await repository.update_password(user_id, new_password_hash)
            
            if success:
                # Invalidate all sessions (force re-login)
                await repository.invalidate_all_user_sessions(user_id)
                self.logger.info(f"Password changed for user: {user_id}")
            
            return success
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user account."""
        async with self._get_session_repo() as (session, repository):
            # Get user
            user = await repository.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")

            # Delete user
            success = await repository.delete(user_id)
            if success:
                self.logger.info(f"User deleted: {user_id}")

            return success

    async def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user ID."""
        try:
            payload = jwt.decode(
                token,
                config.jwt_secret_key,
                algorithms=[config.jwt_algorithm]
            )
            
            if payload.get("type") != "access":
                return None
            
            user_id = payload.get("sub")
            return user_id
            
        except JWTError:
            return None
    
    async def request_password_reset(self, reset_request: PasswordResetRequest) -> bool:
        """Request a password reset by generating a reset token."""
        async with self._get_session_repo() as (session, repository):
            # Get user by email
            user = await repository.get_by_email(reset_request.email.lower())
            
            # Always return True for security (don't reveal if email exists)
            if not user:
                self.logger.warning(f"Password reset requested for non-existent email: {reset_request.email}")
                return True
            
            # Generate reset token (using JWT for simplicity, expires in 1 hour)
            reset_token = self._create_password_reset_token(user.id)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            
            # Store reset token in user record
            await repository.update_password_reset_token(user.id, reset_token, expires_at)
            
            self.logger.info(f"Password reset token generated for user: {user.id}")
            
            # Send email
            if self.email_service:
                await self.email_service.send_password_reset_email(user.email, reset_token, user.name)
            else:
                self.logger.warning("Email service not available, strictly logging token (dev mode only)")
                self.logger.info(f"Reset token for {user.email}: {reset_token}")
            
            return True
    
    def _create_password_reset_token(self, user_id: str) -> str:
        """Create a password reset token."""
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "password_reset"
        }
        return jwt.encode(
            payload,
            config.jwt_secret_key,
            algorithm=config.jwt_algorithm
        )
    
    async def reset_password(self, reset: PasswordReset) -> bool:
        """Reset password using a reset token."""
        async with self._get_session_repo() as (session, repository):
            # Verify reset token
            try:
                payload = jwt.decode(
                    reset.token,
                    config.jwt_secret_key,
                    algorithms=[config.jwt_algorithm]
                )
                
                if payload.get("type") != "password_reset":
                    raise ValueError("Invalid reset token type")
                
                user_id = payload.get("sub")
                if not user_id:
                    raise ValueError("Invalid reset token")
                
            except JWTError:
                raise ValueError("Invalid or expired reset token")
                
            # Get user and verify token matches stored token
            # Need to access DBUser directly to get password_reset_token fields
            from src.database.models import DBUser
            from sqlalchemy import select
            
            stmt = select(DBUser).where(DBUser.id == user_id)
            result = await session.execute(stmt)
            db_user = result.scalar_one_or_none()
            
            if not db_user:
                raise ValueError("User not found")
            
            # Check if token matches and is not expired
            if not db_user.password_reset_token or db_user.password_reset_token != reset.token:
                raise ValueError("Invalid reset token")
            
            # Ensure comparison is done with timezone-aware datetimes
            expires = db_user.password_reset_token_expires
            if expires and expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            
            if not expires or expires < datetime.now(timezone.utc):
                raise ValueError("Reset token has expired")
            
            # Hash new password
            new_password_hash = self._hash_password(reset.new_password)
            
            # Update password and clear reset token
            success = await repository.update_password(user_id, new_password_hash)
            if success:
                await repository.clear_password_reset_token(user_id)
                # Invalidate all sessions (force re-login)
                await repository.invalidate_all_user_sessions(user_id)
                self.logger.info(f"Password reset successful for user: {user_id}")
            
            return success
    
    async def delete_user(self, user_id: str, password: str) -> bool:
        """Delete a user account and all associated data."""
        async with self._get_session_repo() as (session, repository):
            # Get user
            user = await repository.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                raise ValueError("Password is incorrect")
            
            # Delete user (CASCADE will handle related records)
            success = await repository.delete(user_id)
            
            if success:
                self.logger.info(f"Account deleted for user: {user_id}")
            
            return success

