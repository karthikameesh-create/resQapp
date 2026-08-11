from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.rate_limiter import limiter
from app.db.session import get_db
from app.schemas.analytics import (
    DashboardResponse,
    HeatmapResponse,
    TrendResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    responses={
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("60/minute")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    return service.get_dashboard()


@router.get(
    "/trends",
    response_model=TrendResponse,
    responses={
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("60/minute")
def trends(
    request: Request,
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)

    return {
        "trends": service.get_trends()
    }


@router.get(
    "/heatmap",
    response_model=HeatmapResponse,
    responses={
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("60/minute")
def heatmap(
    request: Request,
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)

    return {
        "incidents": service.get_heatmap()
    }