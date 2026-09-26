"""Database mapping for social_accounts."""

from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import DataProvenance, Platform


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    creator_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("creator_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    platform: Mapped[Platform] = mapped_column(
        sa.Enum(Platform, native_enum=False, length=16, validate_strings=True), nullable=False
    )
    external_account_id: Mapped[str] = mapped_column(sa.String(128), nullable=False)
    handle: Mapped[str | None] = mapped_column(sa.String(120), nullable=True)
    profile_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    account_type: Mapped[str | None] = mapped_column(sa.String(24), nullable=True)
    verified_by_oauth: Mapped[bool] = mapped_column(
        sa.Boolean(), nullable=False, server_default=sa.text("false")
    )
    token_ciphertext: Mapped[bytes | None] = mapped_column(sa.LargeBinary(), nullable=True)
    granted_scopes: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    token_expires_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    sync_status: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, server_default=sa.text("'NEVER'")
    )
    data_provenance: Mapped[DataProvenance] = mapped_column(
        sa.Enum(DataProvenance, native_enum=False, length=24, validate_strings=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    __table_args__ = (
        sa.UniqueConstraint("platform", "external_account_id", name="uq_social_platform_account"),
        sa.Index("ix_social_creator", "creator_id"),
    )
