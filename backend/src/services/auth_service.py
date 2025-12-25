"""JWT-based authentication service implementation."""

from datetime import datetime, timezone, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import bcrypt

from ..core.auth_service import AuthService
from ..models.user import (
    User, UserRegister, UserLogin, TokenResponse, UserProfile, 
    UserProfileUpdate, PasswordChange, PasswordResetRequest, PasswordReset
)
from ..database.repositories.user_repository import UserRepository
from ..database.config import database_config
from ..config import config
from ..utils.logger import get_logger
import uuid


class JWTAuthService(AuthService):
    """JWT-based authentication service."""
    
    def __init__(self):
        """Initialize JWT auth service."""
        self.logger = get_logger(__name__)
        self._repository_class = UserRepository
    
    async def initialize(self) -> None:
        """Initialize the service."""
        self.logger.info("JWT Auth Service initialized")
    
    async def cleanup(self) -> None:
        """Cleanup service resources."""
        pass

    @asynccontextmanager
    async def _get_session_repo(self):
        """Context manager for session and repository."""
        async with await database_config.get_session() as session:
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
            # Get user by email
            user = await repository.get_by_email(login.email)
            if not user:
                # Don't reveal if email exists
                raise ValueError("Invalid email or password")
            
            # Check if user is active
            if not user.is_active:
                raise ValueError("Account is disabled")
            
            # Verify password
            if not self._verify_password(login.password, user.password_hash):
                raise ValueError("Invalid email or password")
            
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
    
    async def logout_user(self, refresh_token: str, user_id: str) -> bool:
        """Logout a user by invalidating their refresh token."""
        async with self._get_session_repo() as (session, repository):
            # Verify session belongs to user
            session_obj = await repository.get_session(refresh_token)
            if session_obj and session_obj.user_id == user_id:
                await repository.invalidate_session(refresh_token)
                self.logger.info(f"User logged out: {user_id}")
                return True
        
        return False
    
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
            # In production, send email with reset link here
            # For now, we'll just log it (in production, never log tokens)
            self.logger.debug(f"Reset token for {user.email}: {reset_token[:20]}...")
            
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
            from ..database.models import DBUser
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

