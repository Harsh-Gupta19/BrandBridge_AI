"""Import every model so Alembic sees the complete schema."""

from app.models.agreement import Agreement
from app.models.ai_execution_log import AIExecutionLog
from app.models.brand_product import BrandProduct
from app.models.brand_profile import BrandProfile
from app.models.campaign import Campaign
from app.models.campaign_competitor_policy import CampaignCompetitorPolicy
from app.models.campaign_discovery_policy import CampaignDiscoveryPolicy
from app.models.campaign_requirement import CampaignRequirement
from app.models.collaboration import Collaboration
from app.models.collaboration_outcome import CollaborationOutcome
from app.models.competitor_registry import CompetitorRegistry
from app.models.creator_availability import CreatorAvailability
from app.models.creator_content_cluster import CreatorContentCluster
from app.models.creator_content_item import CreatorContentItem
from app.models.creator_preference import CreatorPreference
from app.models.creator_profile import CreatorProfile
from app.models.creator_representation import CreatorRepresentation
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.eligibility_exclusion import EligibilityExclusion
from app.models.enums import (
    CampaignStatus,
    CollaborationStatus,
    ContentType,
    DataProvenance,
    DiscoveryMode,
    EligibilityStatus,
    InitiatedBy,
    Platform,
    ProposalStatus,
    UserRole,
)
from app.models.experiment_run import ExperimentRun
from app.models.integration_sync_log import IntegrationSyncLog
from app.models.match_evidence import MatchEvidence
from app.models.match_score import MatchScore
from app.models.message import Message
from app.models.model_version import ModelVersion
from app.models.pair_label import PairLabel
from app.models.proposal import Proposal
from app.models.proposal_version import ProposalVersion
from app.models.rate_card_item import RateCardItem
from app.models.social_account import SocialAccount
from app.models.social_metric_snapshot import SocialMetricSnapshot
from app.models.user import User
from app.models.user_role import UserRoleRow
from app.models.wall_comment import WallComment
from app.models.wall_follow import WallFollow
from app.models.wall_post import WallPost
from app.models.wall_reaction import WallReaction

__all__ = [
    "CampaignStatus",
    "CollaborationStatus",
    "InitiatedBy",
    "Platform",
    "ContentType",
    "DataProvenance",
    "DiscoveryMode",
    "EligibilityStatus",
    "AIExecutionLog",
    "Agreement",
    "BrandProduct",
    "BrandProfile",
    "Campaign",
    "CampaignCompetitorPolicy",
    "CampaignDiscoveryPolicy",
    "CampaignRequirement",
    "Collaboration",
    "CollaborationOutcome",
    "CompetitorRegistry",
    "CreatorAvailability",
    "CreatorContentCluster",
    "CreatorContentItem",
    "CreatorPreference",
    "CreatorProfile",
    "CreatorRepresentation",
    "Document",
    "DocumentChunk",
    "EligibilityExclusion",
    "ExperimentRun",
    "IntegrationSyncLog",
    "MatchEvidence",
    "MatchScore",
    "Message",
    "ModelVersion",
    "PairLabel",
    "Proposal",
    "ProposalStatus",
    "ProposalVersion",
    "RateCardItem",
    "SocialAccount",
    "SocialMetricSnapshot",
    "User",
    "UserRole",
    "UserRoleRow",
    "WallComment",
    "WallFollow",
    "WallPost",
    "WallReaction",
]
