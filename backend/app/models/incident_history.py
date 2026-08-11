from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class IncidentHistory(Base):
    __tablename__ = "incident_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action = Column(
        String(50),
        nullable=False,
    )

    field = Column(
        String(50),
        nullable=True,
    )

    old_value = Column(
        Text,
        nullable=True,
    )

    new_value = Column(
        Text,
        nullable=True,
    )

    changed_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    incident = relationship(
        "Incident",
        back_populates="history",
    )

    user = relationship(
        "User",
        foreign_keys=[changed_by],
    )