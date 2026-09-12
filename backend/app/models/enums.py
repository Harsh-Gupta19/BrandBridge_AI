from enum import Enum


class UserRole(str, Enum):
    CREATOR = "CREATOR"
    BRAND = "BRAND"
    ADMIN = "ADMIN"


class ProposalStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
