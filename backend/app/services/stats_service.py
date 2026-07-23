from collections import defaultdict
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import Post

def get_stats(db: Session):

    total = db.scalar(
        select(func.count()).select_from(Post)
    ) or 0

    positive = db.scalar(
        select(func.count()).where(Post.sentiment == "positive")
    ) or 0

    negative = db.scalar(
        select(func.count()).where(Post.sentiment == "negative")
    ) or 0

    neutral = db.scalar(
        select(func.count()).where(Post.sentiment == "neutral")
    ) or 0

    if total == 0:
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


def get_intent_breakdown(db: Session):

    rows = db.execute(
        select(
            Post.intent_category,
            func.count()
        )
        .group_by(Post.intent_category)
        .order_by(func.count().desc())
    ).all()

    return {
        "breakdown": {
            category: count
            for category, count in rows
        }
    }


def get_timeline(db: Session):

    rows = db.execute(
        select(
            func.date(Post.fetched_at),
            Post.sentiment,
            func.count()
        )
        .group_by(
            func.date(Post.fetched_at),
            Post.sentiment
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

    for day, sentiment, count in rows:
        timeline[day][sentiment.lower()] = count

    return {
        "days": [
            {
                "date": str(day),
                **values,
            }
            for day, values in timeline.items()
        ]
    }


