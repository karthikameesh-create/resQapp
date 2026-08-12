from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.rate_limiter import limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
)
from app.schemas.incident_history import IncidentHistoryResponse
from app.services.incident_service import IncidentService
from app.tasks.incident_tasks import analyze_incident_background

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Incident",
    response_description="Incident created successfully",
    responses={
        201: {"description": "Incident created successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Permission denied"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
    },
)
@limiter.limit("30/minute")
def create_incident(
    request: Request,
    background_tasks: BackgroundTasks,
    incident: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = IncidentService(db)
    created_incident = service.create_incident(
        incident,
        current_user,
    )
    background_tasks.add_task(
        analyze_incident_background,
        created_incident.id,
    )
    return created_incident


@router.get(
    "",
    response_model=list[IncidentResponse],
    responses={
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("100/minute")
def get_all_incidents(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    status: str | None = None,
    severity: str | None = None,
    incident_type: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    service = IncidentService(db)

    return service.get_all_incidents(
        skip=skip,
        limit=limit,
        status=status,
        severity=severity,
        incident_type=incident_type,
        search=search,
    )


@router.post(
    "/{incident_id}/retry-ai",
    response_model=IncidentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Retry AI Analysis",
    response_description="AI analysis retry started",
    responses={
        202: {"description": "AI analysis retry started"},
        401: {"description": "Authentication required"},
        403: {"description": "Permission denied"},
        404: {"description": "Incident not found"},
        409: {"description": "Incident is not eligible for AI retry"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("10/minute")
def retry_ai_analysis(
    request: Request,
    incident_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = IncidentService(db)

    return service.retry_ai_analysis(
        incident_id,
        current_user,
        background_tasks,
    )


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    responses={
        404: {"description": "Incident not found"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("100/minute")
def get_incident(
    request: Request,
    incident_id: int,
    db: Session = Depends(get_db),
):
    service = IncidentService(db)
    return service.get_incident(incident_id)


@router.get(
    "/{incident_id}/history",
    response_model=list[IncidentHistoryResponse],
    responses={
        404: {"description": "Incident not found"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("100/minute")
def get_incident_history(
    request: Request,
    incident_id: int,
    db: Session = Depends(get_db),
):
    service = IncidentService(db)

    return service.get_incident_history(incident_id)


@router.put(
    "/{incident_id}",
    response_model=IncidentResponse,
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Permission denied"},
        404: {"description": "Incident not found"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("30/minute")
def update_incident(
    request: Request,
    incident_id: int,
    incident_data: IncidentUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = IncidentService(db)

    return service.update_incident(
        incident_id,
        incident_data,
        current_user,
        background_tasks,
    )


@router.delete(
    "/{incident_id}",
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Permission denied"},
        404: {"description": "Incident not found"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("20/minute")
def delete_incident(
    request: Request,
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = IncidentService(db)

    service.delete_incident(
        incident_id,
        current_user,
    )

    return {"message": "Incident deleted successfully"}