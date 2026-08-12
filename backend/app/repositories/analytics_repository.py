from sqlalchemy import Date, case, cast, func
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

    def incidents_by_priority(self):
        rows = (
            self.db.query(
                Incident.priority,
                func.count(Incident.id),
            )
            .group_by(Incident.priority)
            .all()
        )

        return {
            priority or "Unknown": count
            for priority, count in rows
        }

    def incidents_by_ai_status(self):
        rows = (
            self.db.query(
                Incident.ai_status,
                func.count(Incident.id),
            )
            .group_by(Incident.ai_status)
            .all()
        )

        return {
            ai_status or "Unknown": count
            for ai_status, count in rows
        }

    def average_severity_confidence(self):
        return (
            self.db.query(
                func.avg(Incident.severity_confidence)
            )
            .filter(Incident.severity_confidence.isnot(None))
            .scalar()
        )

    def average_category_confidence(self):
        return (
            self.db.query(
                func.avg(Incident.category_confidence)
            )
            .filter(Incident.category_confidence.isnot(None))
            .scalar()
        )

    def incident_trends(self):
        date_column = cast(Incident.created_at, Date)

        rows = (
            self.db.query(
                date_column.label("date"),
                func.count(Incident.id).label("count"),
                func.sum(
                    case(
                        (Incident.priority == "critical", 1),
                        else_=0,
                    )
                ).label("critical_count"),
                func.sum(
                    case(
                        (Incident.priority == "high", 1),
                        else_=0,
                    )
                ).label("high_count"),
                func.sum(
                    case(
                        (Incident.priority == "medium", 1),
                        else_=0,
                    )
                ).label("medium_count"),
                func.sum(
                    case(
                        (Incident.priority == "low", 1),
                        else_=0,
                    )
                ).label("low_count"),
            )
            .group_by(date_column)
            .order_by(date_column)
            .all()
        )

        return [
            {
                "date": str(date),
                "count": count,
                "critical_count": critical_count or 0,
                "high_count": high_count or 0,
                "medium_count": medium_count or 0,
                "low_count": low_count or 0,
            }
            for (
                date,
                count,
                critical_count,
                high_count,
                medium_count,
                low_count,
            ) in rows
        ]

    def incident_heatmap(self):
        rows = (
            self.db.query(
                Incident.id,
                Incident.latitude,
                Incident.longitude,
                Incident.predicted_severity,
                Incident.predicted_category,
                Incident.priority,
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
                "priority": priority or "Unknown",
                "status": status,
                "created_at": (
                    created_at.isoformat()
                    if created_at
                    else None
                ),
            }
            for (
                incident_id,
                latitude,
                longitude,
                severity,
                category,
                priority,
                status,
                created_at,
            ) in rows
        ]