from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ArticleResponse(BaseModel):
    id: UUID
    title: str
    content: str
    url: str
    source_name: str
    published_at: datetime
    matched_competitors: list = []
    matched_contexts: list = []

    model_config = ConfigDict(from_attributes=True)