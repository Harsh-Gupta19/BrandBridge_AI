"""Database mapping for creator_content_items."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import ContentType, DataProvenance


class CreatorContentItem(Base):
    __tablename__ = "creator_content_items"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    creator_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("creator_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    social_account_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("social_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    external_content_id: Mapped[str | None] = mapped_column(sa.String(160), nullable=True)
    media_type: Mapped[ContentType | None] = mapped_column(
        sa.Enum(ContentType, native_enum=False, length=16, validate_strings=True), nullable=True
    )
    caption: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    transcript: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    organic_or_sponsored: Mapped[str] = mapped_column(
        sa.String(12), nullable=False, server_default=sa.text("'UNKNOWN'")
    )
    brand_entity: Mapped[str | None] = mapped_column(sa.String(160), nullable=True)
    detection_evidence: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    detection_confidence: Mapped[Decimal | None] = mapped_column(sa.Numeric(4, 3), nullable=True)
    metrics_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'{}'"), default=dict
    )
    data_provenance: Mapped[DataProvenance] = mapped_column(
        sa.Enum(DataProvenance, native_enum=False, length=24, validate_strings=True), nullable=False
    )

    __table_args__ = (sa.Index("ix_content_creator_pub", "creator_id", "published_at"),)
