"""
Session and SessionData SQLAlchemy models
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class Session(Base):
    """User session for tracking uploads"""
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), server_default=func.now() + func.cast('2 hours', Text))

    # Relationship to session data
    data = relationship("SessionData", back_populates="session", cascade="all, delete-orphan")


class SessionData(Base):
    """Uploaded vote data for a city within a session"""
    __tablename__ = "session_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    city_key = Column(String(50), nullable=False)
    original_filename = Column(String(255))
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    raw_data = Column(JSONB, nullable=False)
    processed_data = Column(JSONB, nullable=False)

    # Relationship to session
    session = relationship("Session", back_populates="data")

    # Unique constraint on session_id + city_key
    __table_args__ = (
        {'postgresql_ignore_search_path': True},
    )
