from sqlalchemy.orm import Session

from app.models.incident import Incident


class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, incident: Incident) -> Incident:
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        status: str | None = None,
        severity: str | None = None,
        incident_type: str | None = None,
        search: str | None = None,
    ):
        query = self.db.query(Incident)

        if status:
            query = query.filter(Incident.status == status)

        if severity:
            query = query.filter(Incident.severity == severity)

        if incident_type:
            query = query.filter(
                Incident.incident_type == incident_type
            )

        if search:
            query = query.filter(
                Incident.title.ilike(f"%{search}%")
                | Incident.description.ilike(f"%{search}%")
            )

        return (
            query.order_by(Incident.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, incident_id: int):
        return (
            self.db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

    def update(self, incident: Incident) -> Incident:
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def delete(self, incident: Incident) -> None:
        self.db.delete(incident)
        self.db.commit()