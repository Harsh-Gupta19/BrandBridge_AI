"""Database mapping for proposals."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin
from app.models.enums import InitiatedBy, ProposalStatus

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.creator_profile import CreatorProfile


class Proposal(TimestampMixin, Base):
    __tablename__ = "proposals"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("campaigns.id"), nullable=False
    )
    creator_profile_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("creator_profiles.id"), nullable=False
    )
    status: Mapped[ProposalStatus] = mapped_column(
        sa.Enum(ProposalStatus, name="proposal_status", native_enum=False),
        nullable=False,
        default=ProposalStatus.DRAFT,
    )
    message: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    commercial_offer: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2), nullable=True)
    initiated_by: Mapped[InitiatedBy] = mapped_column(
        sa.Enum(InitiatedBy, native_enum=False, length=8, validate_strings=True),
        nullable=False,
        server_default=sa.text("'CREATOR'"),
    )
    match_score_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("match_scores.id"), nullable=True
    )
    deliverables: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    currency: Mapped[str] = mapped_column(
        sa.CHAR(3), nullable=False, server_default=sa.text("'INR'")
    )
    collaboration_model: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, server_default=sa.text("'PAID'")
    )
    available_from: Mapped[date | None] = mapped_column(sa.Date(), nullable=True)
    current_version: Mapped[int] = mapped_column(
        sa.SmallInteger(), nullable=False, server_default=sa.text("1")
    )
    ai_assisted: Mapped[bool] = mapped_column(
        sa.Boolean(), nullable=False, server_default=sa.text("false")
    )
    responded_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        sa.Index("ix_proposal_campaign", "campaign_id", "status"),
        sa.Index("ix_proposal_creator", "creator_profile_id", "status"),
    )

    campaign: Mapped["Campaign"] = relationship(back_populates="proposals")
    creator_profile: Mapped["CreatorProfile"] = relationship(back_populates="proposals")
