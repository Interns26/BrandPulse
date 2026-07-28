from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.database.models import Post, SentimentResult, RssSource, IntentResult

from app.schemas.payloads import AddSource


def get_posts(
    db: Session,
    page: int = 1,
    limit: int = 20,
    priority: str | None = None,
    sentiment: str | None = None,
    source: str | None = None,
    intent: str | None = None
):

    # Load related sentiment and intent tables
    query = select(Post).options(
        joinedload(Post.sentiment_result),
        joinedload(Post.intent_result),
    )

    if priority:
        query = query.where(Post.priority == priority)

    if source:
        query = query.where(Post.source_name == source)

    if sentiment:
        query = query.join(Post.sentiment_result).where(
            SentimentResult.sentiment == sentiment
        )

    if intent:
        query = query.join(IntentResult).where(
            IntentResult.intent_category == intent
        )


    # Count total records
    total = db.scalar(
        select(func.count()).select_from(query.subquery())
    ) or 0


    # Fetch paginated posts
    posts = db.scalars(
        query.order_by(Post.fetched_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()


    # Convert SQLAlchemy objects to API response format
    items = []

    for post in posts:

        sentiment_result = post.sentiment_result
        intent_result = post.intent_result

        items.append(
            {
                "id": post.id,
                "source_name": post.source_name,
                "author": post.author,
                "title": post.title,
                "content": post.content,
                "url": post.url,
                "fetched_at": post.fetched_at,

                "sentiment": (
                    sentiment_result.sentiment
                    if sentiment_result
                    else None
                ),

                "sentiment_confidence": (
                    sentiment_result.confidence
                    if sentiment_result
                    else None
                ),

                "intent_category": (
                    intent_result.intent_category
                    if intent_result
                    else None
                ),

                "intent_description": (
                    intent_result.intent_description
                    if intent_result
                    else None
                ),

                "intent_confidence": (
                    intent_result.confidence
                    if intent_result
                    else None
                ),

                "priority": post.priority,
            }
        )


    return {
        "items": items,
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
        "sources": list(sources)
    }

def add_source(payload:AddSource, db: Session):

    clean_name = payload.name.strip().lstrip("r/")
    display_name = f"r/{clean_name}"

    new_source = RssSource(
        name = clean_name,
        display_name = display_name,
        url = payload.url,
        is_active = payload.is_active,
        fetch_interval_minutes = payload.fetch_interval_minutes,
        last_fetched_at = payload.last_fetched_at
    )

    try:

        db.add(new_source)
        db.commit()
        db.refresh(new_source)

        return new_source

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = f"Source with name {clean_name} already exists"
        )