"""User repository for database operations."""

from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from ..models import DBUser, DBUserSession
from ...models.user import User, UserProfileUpdate
from ...utils.logger import get_logger


class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
        self.logger = get_logger(__name__)
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        try:
            db_user = DBUser.from_model(user)
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
            
            self.logger.info(f"Created user: {user.email}")
            return db_user.to_model()
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating user: {e}", exc_info=True)
            raise
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            stmt = select(DBUser).where(DBUser.id == user_id)
            result = await self.session.execute(stmt)
            db_user = result.scalar_one_or_none()
            
            if db_user:
                return db_user.to_model()
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user {user_id}: {e}", exc_info=True)
            return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            stmt = select(DBUser).where(DBUser.email == email.lower())
            result = await self.session.execute(stmt)
            db_user = result.scalar_one_or_none()
            
            if db_user:
                return db_user.to_model()
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user by email {email}: {e}", exc_info=True)
            return None
    
    async def update(self, user_id: str, updates: UserProfileUpdate) -> Optional[User]:
        """Update user profile."""
        try:
            stmt = (
                update(DBUser)
                .where(DBUser.id == user_id)
                .values(
                    **{k: v for k, v in updates.model_dump(exclude_unset=True).items() if v is not None},
                    updated_at=datetime.utcnow()
                )
            )
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Get updated user
            return await self.get_by_id(user_id)
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
            raise
    
    async def update_password(self, user_id: str, password_hash: str) -> bool:
        """Update user password hash."""
        try:
            stmt = (
                update(DBUser)
                .where(DBUser.id == user_id)
                .values(password_hash=password_hash, updated_at=datetime.utcnow())
            )
            await self.session.execute(stmt)
            await self.session.commit()
            
            self.logger.info(f"Updated password for user {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating password for user {user_id}: {e}", exc_info=True)
            return False
    
    async def create_session(self, user_id: str, refresh_token: str, expires_at: datetime) -> DBUserSession:
        """Create a new user session."""
        try:
            session = DBUserSession(
                user_id=user_id,
                refresh_token=refresh_token,
                expires_at=expires_at
            )
            self.session.add(session)
            await self.session.commit()
            await self.session.refresh(session)
            
            self.logger.debug(f"Created session for user {user_id}")
            return session
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating session: {e}", exc_info=True)
            raise
    
    async def get_session(self, refresh_token: str) -> Optional[DBUserSession]:
        """Get session by refresh token."""
        try:
            stmt = select(DBUserSession).where(
                DBUserSession.refresh_token == refresh_token,
                DBUserSession.is_active == True
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            self.logger.error(f"Error getting session: {e}", exc_info=True)
            return None
    
    async def invalidate_session(self, refresh_token: str) -> bool:
        """Invalidate a session."""
        try:
            stmt = (
                update(DBUserSession)
                .where(DBUserSession.refresh_token == refresh_token)
                .values(is_active=False)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            
            self.logger.debug(f"Invalidated session")
            return True
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error invalidating session: {e}", exc_info=True)
            return False
    
    async def invalidate_all_user_sessions(self, user_id: str) -> bool:
        """Invalidate all sessions for a user."""
        try:
            stmt = (
                update(DBUserSession)
                .where(DBUserSession.user_id == user_id)
                .values(is_active=False)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            
            self.logger.info(f"Invalidated all sessions for user {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error invalidating user sessions: {e}", exc_info=True)
            return False
    
    async def update_password_reset_token(self, user_id: str, token: str, expires_at: datetime) -> bool:
        """Update password reset token for a user."""
        try:
            stmt = (
                update(DBUser)
                .where(DBUser.id == user_id)
                .values(
                    password_reset_token=token,
                    password_reset_token_expires=expires_at,
                    updated_at=datetime.utcnow()
                )
            )
            await self.session.execute(stmt)
            await self.session.commit()
            
            self.logger.info(f"Updated password reset token for user {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating password reset token: {e}", exc_info=True)
            return False
    
    async def clear_password_reset_token(self, user_id: str) -> bool:
        """Clear password reset token for a user."""
        try:
            stmt = (
                update(DBUser)
                .where(DBUser.id == user_id)
                .values(
                    password_reset_token=None,
                    password_reset_token_expires=None,
                    updated_at=datetime.utcnow()
                )
            )
            await self.session.execute(stmt)
            await self.session.commit()
            
            self.logger.info(f"Cleared password reset token for user {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error clearing password reset token: {e}", exc_info=True)
            return False

