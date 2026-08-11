import logging
import time

from app.ai.service import AIService
from app.db.session import SessionLocal
from app.models.incident import Incident
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 2


def analyze_incident_background(
    incident_id: int,
):
    db = SessionLocal()

    try:
        incident = (
            db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

        if incident is None:
            logger.error(
                "Incident %s not found for AI analysis",
                incident_id,
            )
            return

        # Prevent duplicate AI processing
        if incident.ai_status == "processing":
            logger.warning(
                "AI analysis already running for incident_id=%s",
                incident_id,
            )
            return

        # Mark AI processing as started
        incident.ai_status = "processing"
        db.commit()

        logger.info(
            "Starting AI analysis for incident_id=%s",
            incident_id,
        )

        for attempt in range(1, MAX_RETRIES + 1):

            try:
                logger.info(
                    "AI analysis attempt %s/%s for incident_id=%s",
                    attempt,
                    MAX_RETRIES,
                    incident_id,
                )

                analysis = AIService.analyze(
                    incident.description
                )

                incident.predicted_severity = (
                    analysis.predicted_severity
                )

                incident.predicted_category = (
                    analysis.predicted_category
                )

                incident.severity_confidence = (
                    analysis.severity_confidence
                )

                incident.category_confidence = (
                    analysis.category_confidence
                )

                incident.ai_summary = (
                    analysis.summary
                )

                incident.recommended_response = (
                    analysis.recommended_response
                )

                incident.ai_status = "completed"

                db.commit()
                db.refresh(incident)

                # Invalidate analytics cache
                CacheService.delete("dashboard")
                CacheService.delete("trends")
                CacheService.delete("heatmap")

                logger.info(
                    "AI analysis completed successfully "
                    "for incident_id=%s",
                    incident_id,
                )

                return

            except Exception as e:
                db.rollback()

                logger.exception(
                    "AI analysis attempt %s failed "
                    "for incident_id=%s: %s",
                    attempt,
                    incident_id,
                    str(e),
                )

                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)

        # All attempts failed
        incident = (
            db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

        if incident:
            incident.ai_status = "failed"
            db.commit()

        logger.error(
            "AI analysis permanently failed "
            "for incident_id=%s after %s attempts",
            incident_id,
            MAX_RETRIES,
        )

    finally:
        db.close()