# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

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