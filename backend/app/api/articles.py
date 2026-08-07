# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Article, VulnerabilityResult
from app.schemas.article import ArticleResponse

router = APIRouter(
    prefix="/api/articles",
    tags=["Articles"],
)

@router.get("", response_model=list[ArticleResponse])
def get_articles(
    db: Session = Depends(get_db),
):
    # Left join Article with VulnerabilityResult to check if processed by AI pipeline
    results = (
        db.query(
            Article,
            (VulnerabilityResult.id.isnot(None)).label("vulnerability_processed"),
        )
        .outerjoin(VulnerabilityResult, Article.id == VulnerabilityResult.article_id)
        .order_by(Article.published_at.desc())
        .all()
    )

    response = []
    for article, is_processed in results:
        response.append({
            "id": str(article.id),
            "title": article.title,
            "content": article.content,
            "url": article.url,
            "source_name": article.source_name,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "matched_competitors": article.matched_competitors or [],
            "matched_contexts": article.matched_contexts or [],
            "vulnerability_processed": bool(is_processed),
        })

    return response

@router.get("/count")
def get_articles_count(
    db: Session = Depends(get_db),
):
    count = db.query(Article).count()
    return {"articles_count": count}