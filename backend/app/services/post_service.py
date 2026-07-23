from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database.models import Post

def get_posts(
    db: Session,
    page: int = 1,
    limit: int = 20,
    priority: str | None = None,
    sentiment: str | None = None,
    source: str | None = None,
):
    query = select(Post)

    if priority:
        query = query.where(Post.priority == priority)

    if sentiment:
        query = query.where(Post.sentiment == sentiment)

    if source:
        query = query.where(Post.source_name == source)

    total = db.scalar(
        select(func.count()).select_from(query.subquery())
    )

    posts = db.scalars(
        query.offset((page - 1) * limit).limit(limit)
    ).all()

    return {
        "items": posts,
        "total": total,
        "page": page,
        "limit": limit,
    }

def get_sources(db: Session):

    sources = db.scalars(
        select(Post.source_name)
        .distinct()
        .order_by(Post.source_name)
    ).all()

    return {
        "sources": sources
    }

