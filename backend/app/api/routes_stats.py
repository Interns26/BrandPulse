# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.responses import (
    StatsResponse,
    IntentBreakdownResponse,
    TimelineResponse,
)
from app.services import stats_service

router = APIRouter(prefix="/api/stats", tags=["Statistics"])


@router.get("", response_model=StatsResponse)
def get_stats(
    source: str | None = Query(None, description="Filter stats by source_name"),
    db: Session = Depends(get_db),
):
    """
    Returns KPI totals and sentiment percentage breakdowns.
    """
    return stats_service.get_stats(db=db, source=source)


@router.get("/intents", response_model=IntentBreakdownResponse)
def get_intent_breakdown(
    source: str | None = Query(None, description="Filter intent breakdown by source_name"),
    sentiment: str | None = Query(None, description="Filter intent breakdown by sentiment"),
    db: Session = Depends(get_db),
):
    """
    Returns count distribution per intent category for the bar chart.
    """
    return stats_service.get_intent_breakdown(
        db=db, 
        source=source, 
        sentiment=sentiment
    )


@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(
    source: str | None = Query(None, description="Filter timeline trends by source_name"),
    days: int = Query(7, ge=1, le=30, description="Number of historical days"),
    db: Session = Depends(get_db),
):
    """
    Returns sentiment counts aggregated per day for the 7-day trend line chart.
    """
    return stats_service.get_timeline(db=db, source=source, days=days)