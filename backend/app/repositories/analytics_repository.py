from sqlalchemy import Date, cast, func
from sqlalchemy.orm import Session

from app.models.incident import Incident


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def total_incidents(self):
        return self.db.query(func.count(Incident.id)).scalar()

    def incidents_by_status(self):
        rows = (
            self.db.query(
                Incident.status,
                func.count(Incident.id),
            )
            .group_by(Incident.status)
            .all()
        )

        return {status: count for status, count in rows}

    def incidents_by_severity(self):
        rows = (
            self.db.query(
                Incident.predicted_severity,
                func.count(Incident.id),
            )
            .group_by(Incident.predicted_severity)
            .all()
        )

        return {severity or "Unknown": count for severity, count in rows}

    def incidents_by_category(self):
        rows = (
            self.db.query(
                Incident.predicted_category,
                func.count(Incident.id),
            )
            .group_by(Incident.predicted_category)
            .all()
        )

        return {category or "Unknown": count for category, count in rows}

    def incident_trends(self):
        rows = (
            self.db.query(
                cast(Incident.created_at, Date).label("date"),
                func.count(Incident.id).label("count"),
            )
            .group_by(cast(Incident.created_at, Date))
            .order_by(cast(Incident.created_at, Date))
            .all()
        )

        return [
            {
                "date": str(date),
                "count": count,
            }
            for date, count in rows
        ]

    def incident_heatmap(self):
        rows = (
            self.db.query(
                Incident.id,
                Incident.latitude,
                Incident.longitude,
                Incident.predicted_severity,
                Incident.predicted_category,
                Incident.status,
                Incident.created_at,
            )
            .filter(
                Incident.latitude.isnot(None),
                Incident.longitude.isnot(None),
            )
            .all()
        )

        return [
            {
                "id": incident_id,
                "latitude": latitude,
                "longitude": longitude,
                "severity": severity or "Unknown",
                "category": category or "Unknown",
                "status": status,
                "created_at": created_at,
            }
            for (
                incident_id,
                latitude,
                longitude,
                severity,
                category,
                status,
                created_at,
            ) in rows
        ]