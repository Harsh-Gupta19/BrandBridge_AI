"""Database mapping for campaign_requirements."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CampaignRequirement(Base):
    __tablename__ = "campaign_requirements"

    campaign_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("campaigns.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    category: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    target_age_min: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    target_age_max: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    geographies: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    languages: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    platforms: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    content_types: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    preferred_categories: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    mandatory_constraints: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    min_followers: Mapped[int | None] = mapped_column(sa.Integer(), nullable=True)
    max_rate_inr: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2), nullable=True)
    physical_attendance: Mapped[bool] = mapped_column(
        sa.Boolean(), nullable=False, server_default=sa.text("false")
    )
    attendance_city: Mapped[str | None] = mapped_column(sa.String(120), nullable=True)
    extraction_confidence: Mapped[dict[str, Any]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'{}'"), default=dict
    )
    confirmed_by_user_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
