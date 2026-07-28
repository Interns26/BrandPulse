from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.responses import (
    PaginatedPosts,
    SourcesResponse,
)
from app.schemas.payloads import AddSource
from app.services import post_service

router = APIRouter(prefix="/api", tags=["Posts"])


@router.get("/posts", response_model=PaginatedPosts)
def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    priority: str | None = Query(
        None, description="Filter by priority: Low, Medium, High"
    ),
    sentiment: str | None = Query(
        None, description="Filter by sentiment: positive, negative, neutral"
    ),
    source: str | None = Query(
        None, description="Filter by source_name e.g., r_samsung"
    ),
    intent: str | None = Query(
        None, description = "Filter by intent_category e.g., Technical Issues"
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieves paginated posts with eager-loaded sentiment and intent results.
    """
    return post_service.get_posts(
        db=db,
        page=page,
        limit=limit,
        priority=priority,
        sentiment=sentiment,
        source=source,
        intent=intent
    )


@router.get("/sources", response_model=SourcesResponse)
def get_sources(
    db: Session = Depends(get_db),
):
    """
    Retrieves distinct active RSS source names for UI dropdown filtering.
    """
    return post_service.get_sources(db)


@router.post(
    "/sources",
    status_code=status.HTTP_201_CREATED,
    description="Adds a new RSS/Reddit source to be tracked.",
)
def add_source(payload: AddSource, db: Session = Depends(get_db)):

    return post_service.add_source(payload, db)
