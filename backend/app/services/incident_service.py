import logging

from fastapi import HTTPException

from app.core.exceptions import (
    ForbiddenException,
    NotFoundException,
)
from app.models.incident import Incident
from app.models.incident_history import IncidentHistory
from app.models.user import User
from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.services.cache_service import CacheService
from app.tasks.incident_tasks import analyze_incident_background

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

        # Record incident creation in history
        history = IncidentHistory(
            incident_id=incident.id,
            action="created",
            changed_by=current_user.id,
        )

        self.repo.db.add(history)
        self.repo.db.commit()

        logger.info(
            "Incident created with id=%s",
            incident.id,
        )

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
            raise NotFoundException("Incident not found")

        return incident

    def update_incident(
        self,
        incident_id: int,
        incident_data: IncidentUpdate,
        current_user: User,
        background_tasks=None,
    ):
        logger.info(
            "Updating incident=%s",
            incident_id,
        )

        incident = self.repo.get_by_id(incident_id)

        if incident is None:
            logger.error(
                "Incident %s not found",
                incident_id,
            )
            raise NotFoundException("Incident not found")

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

        update_data = incident_data.model_dump(exclude_unset=True)

        # Fields that can change the AI analysis
        ai_relevant_fields = {
            "description",
            "incident_type",
            "severity",
        }

        ai_reanalysis_required = False

        for field, value in update_data.items():
            old_value = getattr(incident, field)

            if old_value != value:
                history = IncidentHistory(
                    incident_id=incident.id,
                    action="updated",
                    field=field,
                    old_value=(
                        str(old_value)
                        if old_value is not None
                        else None
                    ),
                    new_value=(
                        str(value)
                        if value is not None
                        else None
                    ),
                    changed_by=current_user.id,
                )

                self.repo.db.add(history)

                setattr(incident, field, value)

                if field in ai_relevant_fields:
                    ai_reanalysis_required = True

        # If an AI-relevant field changed, mark the analysis as pending
        if ai_reanalysis_required:
            incident.ai_status = "pending"

            incident.predicted_severity = None
            incident.severity_confidence = None
            incident.predicted_category = None
            incident.category_confidence = None
            incident.ai_summary = None
            incident.recommended_response = None

            # Reset priority until the new AI analysis completes
            incident.priority = "low"

            logger.info(
                "AI re-analysis required for incident=%s",
                incident_id,
            )

        logger.info(
            "Incident updated=%s",
            incident_id,
        )

        incident = self.repo.update(incident)

        CacheService.delete("dashboard")
        CacheService.delete("trends")
        CacheService.delete("heatmap")

        # Start AI analysis after the database update
        if ai_reanalysis_required and background_tasks is not None:
            background_tasks.add_task(
                analyze_incident_background,
                incident.id,
            )

        return incident

    def delete_incident(
        self,
        incident_id: int,
        current_user: User,
    ):
        logger.info(
            "Deleting incident=%s",
            incident_id,
        )

        incident = self.repo.get_by_id(incident_id)

        if incident is None:
            logger.error(
                "Incident %s not found",
                incident_id,
            )
            raise NotFoundException("Incident not found")

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

        # Record deletion in audit history
        history = IncidentHistory(
            incident_id=incident.id,
            action="deleted",
            changed_by=current_user.id,
        )
        self.repo.db.add(history)

        # Delete incident
        self.repo.db.delete(incident)

        # Commit both operations together
        self.repo.db.commit()

        CacheService.delete("dashboard")
        CacheService.delete("trends")
        CacheService.delete("heatmap")

        logger.info(
            "Incident deleted=%s",
            incident_id,
        )

    def retry_ai_analysis(
        self,
        incident_id: int,
        current_user: User,
        background_tasks,
    ):
        incident = self.repo.get_by_id(incident_id)

        if incident is None:
            raise NotFoundException("Incident not found")

        # Only the reporter or admin can retry AI processing
        if (
            incident.reporter_id != current_user.id
            and current_user.role != "admin"
        ):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to retry AI analysis",
            )

        # Retry should only be available for failed processing
        if incident.ai_status != "failed":
            raise HTTPException(
                status_code=409,
                detail=(
                    f"AI retry is only available for failed incidents. "
                    f"Current status: {incident.ai_status}"
                ),
            )

        # Reset AI fields
        incident.ai_status = "pending"
        incident.predicted_severity = None
        incident.predicted_category = None
        incident.ai_summary = None
        incident.recommended_response = None

        incident = self.repo.update(incident)

        # Start background AI processing again
        background_tasks.add_task(
            analyze_incident_background,
            incident.id,
        )

        return incident

    def get_incident_history(self, incident_id: int):
        logger.info(
            "Fetching history for incident=%s",
            incident_id,
        )

        incident = self.repo.get_by_id(incident_id)

        if incident is None:
            raise NotFoundException("Incident not found")

        return self.repo.get_history(incident_id)