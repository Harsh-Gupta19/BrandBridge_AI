"""Database mapping for pair_labels."""

from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PairLabel(Base):
    __tablename__ = "pair_labels"

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
    rater_id: Mapped[str] = mapped_column(sa.String(40), nullable=False)
    brand_rating: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    creator_rating: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    mutually_relevant: Mapped[bool | None] = mapped_column(
        sa.Boolean(),
        sa.Computed("brand_rating >= 2 AND creator_rating >= 2", persisted=True),
        nullable=True,
    )
    rationale: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    label_source: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    rubric_version: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    __table_args__ = (
        sa.CheckConstraint("brand_rating BETWEEN 0 AND 3", name="ck_pair_brand_rating"),
        sa.CheckConstraint("creator_rating BETWEEN 0 AND 3", name="ck_pair_creator_rating"),
        sa.UniqueConstraint(
            "campaign_id", "creator_id", "rater_id", "rubric_version", name="uq_pair_rater_rubric"
        ),
    )
