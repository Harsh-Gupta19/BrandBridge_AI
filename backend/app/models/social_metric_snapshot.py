"""Database mapping for social_metric_snapshots."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import DataProvenance


class SocialMetricSnapshot(Base):
    __tablename__ = "social_metric_snapshots"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    social_account_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("social_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    captured_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
    followers: Mapped[int | None] = mapped_column(sa.Integer(), nullable=True)
    total_content: Mapped[int | None] = mapped_column(sa.Integer(), nullable=True)
    total_views: Mapped[int | None] = mapped_column(sa.BigInteger(), nullable=True)
    sample_size: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    sample_window_start: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    sample_window_end: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    average_views: Mapped[Decimal | None] = mapped_column(sa.Numeric(14, 2), nullable=True)
    median_views: Mapped[Decimal | None] = mapped_column(sa.Numeric(14, 2), nullable=True)
    average_likes: Mapped[Decimal | None] = mapped_column(sa.Numeric(14, 2), nullable=True)
    average_comments: Mapped[Decimal | None] = mapped_column(sa.Numeric(14, 2), nullable=True)
    engagement_rate: Mapped[Decimal | None] = mapped_column(sa.Numeric(6, 4), nullable=True)
    posts_last_30_days: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    platform_specific: Mapped[dict[str, Any]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'{}'"), default=dict
    )
    data_provenance: Mapped[DataProvenance] = mapped_column(
        sa.Enum(DataProvenance, native_enum=False, length=24, validate_strings=True), nullable=False
    )

    __table_args__ = (sa.Index("ix_snap_account_time", "social_account_id", "captured_at"),)
