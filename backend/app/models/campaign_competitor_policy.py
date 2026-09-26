"""Database mapping for campaign_competitor_policies."""

from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CampaignCompetitorPolicy(Base):
    __tablename__ = "campaign_competitor_policies"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    competitor_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("competitor_registry.id"), nullable=False
    )
    association_type: Mapped[str] = mapped_column(
        sa.String(32), nullable=False, server_default=sa.text("'PAID_ONLY'")
    )
    lookback_days: Mapped[int] = mapped_column(
        sa.SmallInteger(), nullable=False, server_default=sa.text("180")
    )
    action: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, server_default=sa.text("'EXCLUDE'")
    )
