# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

import hashlib
from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import Article


def generate_content_hash(content: str) -> str:
    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def save_article(
    db: Session,
    article_data: dict,
) -> Article:

    content_hash = generate_content_hash(
        article_data["content"]
    )

    # Check for an existing article by URL
    existing_article = (
        db.query(Article)
        .filter(Article.url == article_data["url"])
        .first()
    )

    if existing_article:
        return existing_article

    # Check for duplicate content
    existing_article = (
        db.query(Article)
        .filter(Article.content_hash == content_hash)
        .first()
    )

    if existing_article:
        return existing_article

    try:
        article = Article(
            title=article_data["title"],
            content=article_data["content"],
            url=article_data["url"],
            source_name=article_data["source_name"],
            published_at=datetime.fromisoformat(
                article_data["published_at"]
            ),
            matched_competitors=article_data.get(
                "matched_competitors", []
            ),
            matched_contexts=article_data.get(
                "matched_contexts", []
            ),
            content_hash=content_hash,
        )

        db.add(article)
        db.commit()
        db.refresh(article)

        return article

    except Exception:
        db.rollback()
        raise