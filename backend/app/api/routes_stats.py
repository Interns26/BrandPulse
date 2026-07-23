from fastapi import APIRouter, Depends
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
    db: Session = Depends(get_db),
):
    return stats_service.get_stats(db)


@router.get("/intents", response_model=IntentBreakdownResponse)
def get_intent_breakdown(
    db: Session = Depends(get_db),
):
    return stats_service.get_intent_breakdown(db)


@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(
    db: Session = Depends(get_db),
):
    return stats_service.get_timeline(db)