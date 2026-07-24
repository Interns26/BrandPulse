from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PostRead(BaseModel):
    id: UUID

    source_name: str

    author: Optional[str] = None
    title: Optional[str] = None
    content: str
    url: Optional[str] = None

    fetched_at: datetime

    sentiment: Optional[str] = None
    sentiment_confidence: Optional[float] = None

    intent_category: Optional[str] = None
    intent_description: Optional[str] = None
    intent_confidence: Optional[float] = None

    priority: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedPosts(BaseModel):
    items: list[PostRead]
    total: int
    page: int
    limit: int


class StatsResponse(BaseModel):
    total: int

    positive: int
    neutral: int
    negative: int

    positivePct: int
    neutralPct: int
    negativePct: int


class IntentBreakdownResponse(BaseModel):
    breakdown: dict[str, int]


class TimelineDay(BaseModel):
    date: str
    positive: int
    neutral: int
    negative: int


class TimelineResponse(BaseModel):
    days: list[TimelineDay]


class SourcesResponse(BaseModel):
    sources: list[str]