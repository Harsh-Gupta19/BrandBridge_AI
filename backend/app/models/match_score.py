"""Database mapping for match_scores."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import EligibilityStatus


class MatchScore(Base):
    __tablename__ = "match_scores"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    creator_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("creator_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    direction: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    eligibility_status: Mapped[EligibilityStatus] = mapped_column(
        sa.Enum(EligibilityStatus, native_enum=False, length=20, validate_strings=True),
        nullable=False,
    )
    structured_score: Mapped[Decimal | None] = mapped_column(sa.Numeric(6, 5), nullable=True)
    semantic_score: Mapped[Decimal | None] = mapped_column(sa.Numeric(6, 5), nullable=True)
    brand_side_score: Mapped[Decimal | None] = mapped_column(sa.Numeric(6, 5), nullable=True)
    creator_side_score: Mapped[Decimal | None] = mapped_column(sa.Numeric(6, 5), nullable=True)
    reciprocal_score: Mapped[Decimal | None] = mapped_column(sa.Numeric(6, 5), nullable=True)
    reranked_score: Mapped[Decimal | None] = mapped_column(sa.Numeric(6, 5), nullable=True)
    final_rank: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    feature_version: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    model_version: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    representation_version: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    scoring_profile: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    components: Mapped[dict[str, Any]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'{}'"), default=dict
    )
    computed_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "campaign_id",
            "creator_id",
            "direction",
            "model_version",
            "feature_version",
            name="uq_match_pair_direction_versions",
        ),
        sa.Index("ix_match_creator", "creator_id", "direction", "reciprocal_score"),
        sa.Index("ix_match_rank", "campaign_id", "direction", "final_rank"),
    )
