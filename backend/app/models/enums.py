from enum import Enum


class UserRole(str, Enum):
    CITIZEN = "citizen"
    RESPONDER = "responder"
    ADMIN = "admin"