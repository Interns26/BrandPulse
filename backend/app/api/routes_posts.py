from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.responses import (
    PaginatedPosts,
    SourcesResponse,
)
from app.services import post_service

router = APIRouter(prefix="/api", tags=["Posts"])


@router.get("/posts", response_model=PaginatedPosts)
def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    priority: str | None = None,
    sentiment: str | None = None,
    source: str | None = None,
    db: Session = Depends(get_db),
):
    return post_service.get_posts(
        db=db,
        page=page,
        limit=limit,
        priority=priority,
        sentiment=sentiment,
        source=source,
    )


@router.get("/sources", response_model=SourcesResponse)
def get_sources(
    db: Session = Depends(get_db),
):
    return post_service.get_sources(db)