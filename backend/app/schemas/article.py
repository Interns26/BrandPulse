from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ArticleResponse(BaseModel):
    id: str
    title: str
    content: str
    url: str
    source_name: str
    published_at: str | None = None
    matched_competitors: list[str] = []
    matched_contexts: list[str] = []
    vulnerability_processed: bool

    class Config:
        from_attributes = True