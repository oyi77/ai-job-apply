"""
Security enhancements for authentication.

Includes:
- Password history tracking
- Account lockout improvements
"""

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from loguru import logger

from src.models.user import User, PasswordHistory
from src.core.security import get_password_hash, verify_password


class SecurityService:
    """Service for handling security-related operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logger.bind(service="SecurityService")
    
    async def track_password_history(self, user_id: str, hashed_password: str):
        """Add password to history tracking."""
        try:
            # Check history limit (e.g., keep last 5 passwords)
            stmt = select(PasswordHistory).where(PasswordHistory.user_id == user_id).order_by(PasswordHistory.created_at.desc())
            result = await self.session.execute(stmt)
            history = result.scalars().all()
            
            if len(history) >= 5:
                # Remove oldest
                oldest = history[-1]
                await self.session.delete(oldest)
            
            # Add new password
            new_entry = PasswordHistory(
                user_id=user_id,
                password_hash=hashed_password,
                created_at=datetime.utcnow()
            )
            self.session.add(new_entry)
            await self.session.commit()
            
        except Exception as e:
            self.logger.error(f"Error tracking password history: {e}")
            await self.session.rollback()
            # Non-blocking error
    
    async def is_password_reused(self, user_id: str, new_password: str) -> bool:
        """Check if new password was used recently."""
        try:
            stmt = select(PasswordHistory).where(PasswordHistory.user_id == user_id)
            result = await self.session.execute(stmt)
            history = result.scalars().all()
            
            for entry in history:
                if verify_password(new_password, entry.password_hash):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking password reuse: {e}")
            return False
