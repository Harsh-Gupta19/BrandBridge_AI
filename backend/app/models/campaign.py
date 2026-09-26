"""Database mapping for campaigns."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin
from app.models.enums import CampaignStatus

if TYPE_CHECKING:
    from app.models.brand_profile import BrandProfile
    from app.models.proposal import Proposal


class Campaign(TimestampMixin, Base):
    __tablename__ = "campaigns"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    brand_profile_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("brand_profiles.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    brief: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    budget_amount: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2), nullable=True)
    target_country: Mapped[str | None] = mapped_column(sa.String(120), nullable=True)
    target_audience: Mapped[dict[str, Any]] = mapped_column(
        sa.JSON(), nullable=False, server_default=sa.text("'{}'::json"), default=dict
    )
    preferred_platforms: Mapped[list[str]] = mapped_column(
        sa.JSON(), nullable=False, server_default=sa.text("'[]'::json"), default=list
    )
    creator_categories: Mapped[list[str]] = mapped_column(
        sa.JSON(), nullable=False, server_default=sa.text("'[]'::json"), default=list
    )
    content_formats: Mapped[list[str]] = mapped_column(
        sa.JSON(), nullable=False, server_default=sa.text("'[]'::json"), default=list
    )
    raw_brief: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    objective: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    status: Mapped[CampaignStatus] = mapped_column(
        sa.Enum(CampaignStatus, native_enum=False, length=16, validate_strings=True),
        nullable=False,
        server_default=sa.text("'DRAFT'"),
    )
    budget_min: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2), nullable=True)
    budget_max: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(
        sa.CHAR(3), nullable=False, server_default=sa.text("'INR'")
    )
    starts_on: Mapped[date | None] = mapped_column(sa.Date(), nullable=True)
    ends_on: Mapped[date | None] = mapped_column(sa.Date(), nullable=True)
    parser_version: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    parsed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    __table_args__ = (sa.Index("ix_campaign_status", "status", "published_at"),)

    brand_profile: Mapped["BrandProfile"] = relationship(back_populates="campaigns")
    proposals: Mapped[list["Proposal"]] = relationship(back_populates="campaign")
