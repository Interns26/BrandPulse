import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .session import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False, default="reddit_rss")
    source_name = Column(String(100))
    external_id = Column(String(255))
    author = Column(String(255))
    title = Column(Text)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), unique=True, nullable=False)
    url = Column(Text)
    
    # Using callables with timezone-aware UTC
    fetched_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    sentiment_result = relationship(
        "SentimentResult", 
        back_populates="post", 
        uselist=False, 
        cascade="all, delete-orphan"
    )
    intent_result = relationship(
        "IntentResult", 
        back_populates="post", 
        uselist=False, 
        cascade="all, delete-orphan"
    )


class SentimentResult(Base):
    __tablename__ = "sentiment_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), unique=True)
    sentiment = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    scores = Column(JSON)
    processed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    post = relationship("Post", back_populates="sentiment_result")


class IntentResult(Base):
    __tablename__ = "intent_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), unique=True)
    intent_category = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    scores = Column(JSON)
    processed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    post = relationship("Post", back_populates="intent_result")


class RssSource(Base):
    __tablename__ = "rss_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    fetch_interval_minutes = Column(Integer, default=30)
    last_fetched_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IngestionLog(Base):
    __tablename__ = "ingestion_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)
    posts_fetched = Column(Integer, default=0)
    posts_new = Column(Integer, default=0)
    errors = Column(Text)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))