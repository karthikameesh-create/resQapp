from fastapi import HTTPException

from app.ai.service import AIService
from app.models.incident import Incident
from app.models.user import User
from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import IncidentCreate, IncidentUpdate


class IncidentService:
    def __init__(self, db):
        self.repo = IncidentRepository(db)

    def create_incident(
        self,
        incident_data: IncidentCreate,
        current_user: User,
    ):
        # Create incident
        incident = Incident(
            title=incident_data.title,
            description=incident_data.description,
            incident_type=incident_data.incident_type,
            latitude=incident_data.latitude,
            longitude=incident_data.longitude,
            reporter_id=current_user.id,
        )

        # Save incident first
        incident = self.repo.create(incident)

        # Analyze using Gemini
        analysis = AIService.analyze(incident.description)

        # Store AI analysis
        incident.predicted_severity = analysis.predicted_severity
        incident.predicted_category = analysis.predicted_category
        incident.ai_summary = analysis.summary
        incident.recommended_response = analysis.recommended_response

        # Save AI fields
        incident = self.repo.update(incident)

        return incident

    def get_all_incidents(
        self,
        skip: int = 0,
        limit: int = 10,
        status: str | None = None,
        severity: str | None = None,
        incident_type: str | None = None,
        search: str | None = None,
    ):
        return self.repo.get_all(
            skip=skip,
            limit=limit,
            status=status,
            severity=severity,
            incident_type=incident_type,
            search=search,
        )

    def get_incident(self, incident_id: int):
        return self.repo.get_by_id(incident_id)

    def update_incident(
        self,
        incident_id: int,
        incident_data: IncidentUpdate,
        current_user: User,
    ):
        incident = self.repo.get_by_id(incident_id)

        if incident is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        if (
            incident.reporter_id != current_user.id
            and current_user.role != "admin"
        ):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to update this incident",
            )

        update_data = incident_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(incident, field, value)

        return self.repo.update(incident)

    def delete_incident(
        self,
        incident_id: int,
        current_user: User,
    ):
        incident = self.repo.get_by_id(incident_id)

        if incident is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        if (
            incident.reporter_id != current_user.id
            and current_user.role != "admin"
        ):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete this incident",
            )

        self.repo.delete(incident)