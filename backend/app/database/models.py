import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
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
    fetched_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # ==========================
    # Priority (derived from sentiment + intent)
    # ==========================
    priority = Column(String(20), nullable=False)

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

    # Indexes for fast queries
    __table_args__ = (
        Index("idx_posts_fetched_at", "fetched_at"),
        Index("idx_posts_source_name", "source_name"),
        Index("idx_posts_content_hash", "content_hash"),
        Index("idx_posts_source_fetched", "source_name", "fetched_at"),
        Index("idx_posts_priority", "priority"),
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

    # Indexes for fast queries
    __table_args__ = (
        Index("idx_sentiment_post_id", "post_id"),
        Index("idx_sentiment_sentiment", "sentiment"),
        Index("idx_sentiment_post_sentiment", "post_id", "sentiment"),
    )


class IntentResult(Base):
    __tablename__ = "intent_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        unique=True
    )

    intent_category = Column(String(50), nullable=False)

    intent_description = Column(
        Text,
        nullable=True
    )

    confidence = Column(Float, nullable=False)

    scores = Column(JSON)

    processed_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    post = relationship(
        "Post",
        back_populates="intent_result"
    )

    __table_args__ = (
        Index("idx_intent_post_id", "post_id"),
        Index("idx_intent_category", "intent_category"),
        Index("idx_intent_post_category", "post_id", "intent_category"),
    )

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

    # Indexes for fast queries
    __table_args__ = (
        Index("idx_rss_sources_active", "is_active"),
        Index("idx_rss_sources_name", "name"),
    )


class IngestionLog(Base):
    __tablename__ = "ingestion_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)
    posts_fetched = Column(Integer, default=0)
    posts_new = Column(Integer, default=0)
    errors = Column(Text)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))

    # Indexes for fast queries
    __table_args__ = (
        Index("idx_ingestion_logs_started", "started_at"),
        Index("idx_ingestion_logs_source", "source"),
    )