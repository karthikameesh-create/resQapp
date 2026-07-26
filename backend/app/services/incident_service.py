import logging

from app.ai.service import AIService
from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
)
from app.models.incident import Incident
from app.models.user import User
from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import IncidentCreate, IncidentUpdate

logger = logging.getLogger(__name__)


class IncidentService:
    def __init__(self, db):
        self.repo = IncidentRepository(db)

    def create_incident(
        self,
        incident_data: IncidentCreate,
        current_user: User,
    ):
        logger.info(
            "Creating incident for user_id=%s",
            current_user.id,
        )

        incident = Incident(
            title=incident_data.title,
            description=incident_data.description,
            incident_type=incident_data.incident_type,
            latitude=incident_data.latitude,
            longitude=incident_data.longitude,
            reporter_id=current_user.id,
        )

        incident = self.repo.create(incident)

        logger.info(
            "Incident created with id=%s",
            incident.id,
        )

        logger.info(
            "Starting AI analysis for incident=%s",
            incident.id,
        )

        analysis = AIService.analyze(
            incident.description
        )

        logger.info(
            "AI analysis completed for incident=%s",
            incident.id,
        )

        incident.predicted_severity = analysis.predicted_severity
        incident.predicted_category = analysis.predicted_category
        incident.ai_summary = analysis.summary
        incident.recommended_response = (
            analysis.recommended_response
        )

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
        logger.info("Fetching incidents")

        return self.repo.get_all(
            skip=skip,
            limit=limit,
            status=status,
            severity=severity,
            incident_type=incident_type,
            search=search,
        )

    def get_incident(self, incident_id: int):
        logger.info(
            "Fetching incident=%s",
            incident_id,
        )

        incident = self.repo.get_by_id(incident_id)

        if incident is None:
            logger.error(
                "Incident %s not found",
                incident_id,
            )
            raise NotFoundException(
                "Incident not found"
            )

        return incident

    def update_incident(
        self,
        incident_id: int,
        incident_data: IncidentUpdate,
        current_user: User,
    ):
        logger.info(
            "Updating incident=%s",
            incident_id,
        )

        incident = self.repo.get_by_id(
            incident_id
        )

        if incident is None:
            logger.error(
                "Incident %s not found",
                incident_id,
            )
            raise NotFoundException(
                "Incident not found"
            )

        if (
            incident.reporter_id != current_user.id
            and current_user.role != "admin"
        ):
            logger.warning(
                "Unauthorized update by user=%s on incident=%s",
                current_user.id,
                incident_id,
            )

            raise ForbiddenException(
                "Not authorized to update this incident"
            )

        update_data = incident_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                incident,
                field,
                value,
            )

        logger.info(
            "Incident updated=%s",
            incident_id,
        )

        return self.repo.update(
            incident
        )

    def delete_incident(
        self,
        incident_id: int,
        current_user: User,
    ):
        logger.info(
            "Deleting incident=%s",
            incident_id,
        )

        incident = self.repo.get_by_id(
            incident_id
        )

        if incident is None:
            logger.error(
                "Incident %s not found",
                incident_id,
            )
            raise NotFoundException(
                "Incident not found"
            )

        if (
            incident.reporter_id != current_user.id
            and current_user.role != "admin"
        ):
            logger.warning(
                "Unauthorized delete by user=%s on incident=%s",
                current_user.id,
                incident_id,
            )

            raise ForbiddenException(
                "Not authorized to delete this incident"
            )

        self.repo.delete(
            incident
        )

        logger.info(
            "Incident deleted=%s",
            incident_id,
        )