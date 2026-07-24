from collections import defaultdict
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import Post, SentimentResult, IntentResult


def get_stats(db: Session, source: str | None = None):
    # Single efficient query using conditional aggregation
    stmt = (
        select(
            func.count(Post.id).label("total"),
            func.count().filter(SentimentResult.sentiment == "positive").label("positive"),
            func.count().filter(SentimentResult.sentiment == "negative").label("negative"),
            func.count().filter(SentimentResult.sentiment == "neutral").label("neutral"),
        )
        .outerjoin(Post.sentiment_result)
    )

    if source:
        stmt = stmt.where(Post.source_name == source)

    row = db.execute(stmt).one()
    total, positive, negative, neutral = row.total, row.positive, row.negative, row.neutral

    if not total:
        return {
            "total": 0,
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "positivePct": 0,
            "negativePct": 0,
            "neutralPct": 0,
        }

    return {
        "total": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "positivePct": round(positive * 100 / total),
        "negativePct": round(negative * 100 / total),
        "neutralPct": round(neutral * 100 / total),
    }


def get_intent_breakdown(db: Session, source: str | None = None, sentiment: str | None = None):
    stmt = (
        select(
            IntentResult.intent_category,
            func.count(Post.id)
        )
        .join(Post.intent_result)
    )

    if sentiment:
        stmt = stmt.join(Post.sentiment_result).where(SentimentResult.sentiment == sentiment)

    if source:
        stmt = stmt.where(Post.source_name == source)

    rows = db.execute(
        stmt.group_by(IntentResult.intent_category)
        .order_by(func.count(Post.id).desc())
    ).all()

    return {
        "breakdown": {
            category: count for category, count in rows if category
        }
    }


def get_timeline(db: Session, source: str | None = None, days: int = 7):
    stmt = (
        select(
            func.date(Post.fetched_at).label("fetched_date"),
            SentimentResult.sentiment,
            func.count(Post.id)
        )
        .join(Post.sentiment_result)
    )

    if source:
        stmt = stmt.where(Post.source_name == source)

    rows = db.execute(
        stmt.group_by(
            func.date(Post.fetched_at),
            SentimentResult.sentiment
        )
        .order_by(func.date(Post.fetched_at))
    ).all()

    timeline = defaultdict(
        lambda: {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
        }
    )

    for day, sentiment_val, count in rows:
        if day and sentiment_val:
            timeline[str(day)][sentiment_val.lower()] = count

    return {
        "days": [
            {
                "date": date_str,
                **values,
            }
            for date_str, values in timeline.items()
        ]
    }