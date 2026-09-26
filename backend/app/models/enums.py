from enum import StrEnum


class UserRole(StrEnum):
    CREATOR = "CREATOR"
    BRAND = "BRAND"
    ADMIN = "ADMIN"


class ProposalStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    REVIEWING = "REVIEWING"
    COUNTER_OFFER = "COUNTER_OFFER"
    WITHDRAWN = "WITHDRAWN"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class CampaignStatus(StrEnum):
    DRAFT = "DRAFT"
    PARSED = "PARSED"
    READY = "READY"
    PUBLISHED = "PUBLISHED"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class CollaborationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    IN_PRODUCTION = "IN_PRODUCTION"
    IN_REVIEW = "IN_REVIEW"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InitiatedBy(StrEnum):
    CREATOR = "CREATOR"
    BRAND = "BRAND"


class Platform(StrEnum):
    YOUTUBE = "YOUTUBE"
    INSTAGRAM = "INSTAGRAM"
    BLUESKY = "BLUESKY"
    MANUAL = "MANUAL"


class ContentType(StrEnum):
    REEL = "REEL"
    STORY = "STORY"
    POST = "POST"
    SHORT = "SHORT"
    VIDEO = "VIDEO"
    CAROUSEL = "CAROUSEL"
    OTHER = "OTHER"


class DataProvenance(StrEnum):
    CREATOR_PROVIDED = "CREATOR_PROVIDED"
    AUTHORIZED_API = "AUTHORIZED_API"
    PUBLIC_OBSERVABLE = "PUBLIC_OBSERVABLE"
    AI_DERIVED = "AI_DERIVED"
    SYNTHETIC = "SYNTHETIC"


class DiscoveryMode(StrEnum):
    CONVENTIONAL = "CONVENTIONAL"
    ADJACENT = "ADJACENT"
    FRESH_TO_VERTICAL = "FRESH_TO_VERTICAL"
    NO_PREFERENCE = "NO_PREFERENCE"


class EligibilityStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
