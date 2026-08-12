from enum import Enum


class UserRole(str, Enum):
    CITIZEN = "citizen"
    RESPONDER = "responder"
    ADMIN = "admin"


class IncidentPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"