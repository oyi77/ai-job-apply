from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime
import uuid

from ..database.config import Base

class PasswordHistory(Base):
    __tablename__ = "password_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
