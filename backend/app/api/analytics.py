from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
)
def dashboard(db: Session = Depends(get_db)):
    service = AnalyticsService(db)
    return service.get_dashboard()


@router.get(
    "/trends",
    response_model=TrendResponse,
)
def trends(db: Session = Depends(get_db)):
    service = AnalyticsService(db)

    return {
        "trends": service.get_trends()
    }


@router.get(
    "/heatmap",
    response_model=HeatmapResponse,
)
def heatmap(db: Session = Depends(get_db)):
    service = AnalyticsService(db)

    return {
        "incidents": service.get_heatmap()
    }