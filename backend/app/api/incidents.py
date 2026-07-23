from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
)
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("", response_model=IncidentResponse)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = IncidentService(db)
    return service.create_incident(incident, current_user)


@router.get("", response_model=list[IncidentResponse])
def get_all_incidents(
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


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    service = IncidentService(db)

    incident = service.get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    incident_data: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = IncidentService(db)

    return service.update_incident(
        incident_id,
        incident_data,
        current_user,
    )


@router.delete("/{incident_id}")
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = IncidentService(db)

    service.delete_incident(
        incident_id,
        current_user,
    )

    return {
        "message": "Incident deleted successfully"
    }