import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID
from .session import Base


class Post(Base):
    __tablename__ = "posts"

    # ==========================
    # Primary Key
    # ==========================
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ==========================
    # Source Information
    # ==========================
    source = Column(String(50), nullable=False, index=True)
    source_name = Column(String(100), nullable=False, index=True)
    external_id = Column(String(255), nullable=False, unique=True)

    # ==========================
    # Original Reddit Post
    # ==========================
    author = Column(String(255))
    title = Column(Text)
    content = Column(Text, nullable=False)
    ai_input_text = Column(Text, nullable=False)
    url = Column(Text)
    content_hash = Column(String(64), nullable=False, unique=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False)

    # ==========================
    # AI Analysis
    # ==========================
    sentiment = Column(String(20), nullable=False, index=True)
    sentiment_confidence = Column(Float, nullable=False)
    intent_category = Column(String(100), nullable=False, index=True)
    intent_description = Column(Text, nullable=False)
    intent_confidence = Column(Float, nullable=False)
    priority = Column(String(20), nullable=False, index=True)

    # ==========================
    # Backend Metadata
    # ==========================
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )