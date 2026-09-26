"""Database mapping for campaign_discovery_policy."""

from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import DiscoveryMode


class CampaignDiscoveryPolicy(Base):
    __tablename__ = "campaign_discovery_policy"

    campaign_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("campaigns.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    mode: Mapped[DiscoveryMode] = mapped_column(
        sa.Enum(DiscoveryMode, native_enum=False, length=24, validate_strings=True),
        nullable=False,
        server_default=sa.text("'NO_PREFERENCE'"),
    )
    vertical_experience: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, server_default=sa.text("'PREFERRED'")
    )
    novelty_weight: Mapped[Decimal] = mapped_column(
        sa.Numeric(4, 3), nullable=False, server_default=sa.text("0.000")
    )
    min_transferable_fit: Mapped[Decimal] = mapped_column(
        sa.Numeric(4, 3), nullable=False, server_default=sa.text("0.620")
    )
    enable_fairness_rerank: Mapped[bool] = mapped_column(
        sa.Boolean(), nullable=False, server_default=sa.text("false")
    )
    diversity_lambda: Mapped[Decimal] = mapped_column(
        sa.Numeric(4, 3), nullable=False, server_default=sa.text("0.300")
    )
