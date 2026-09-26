"""Database mapping for integration_sync_logs."""

from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import Platform


class IntegrationSyncLog(Base):
    __tablename__ = "integration_sync_logs"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    social_account_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("social_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    platform: Mapped[Platform] = mapped_column(
        sa.Enum(Platform, native_enum=False, length=16, validate_strings=True), nullable=False
    )
    request_class: Mapped[str] = mapped_column(sa.String(40), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    error_category: Mapped[str | None] = mapped_column(sa.String(40), nullable=True)
    error_detail: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(sa.Integer(), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    __table_args__ = (sa.Index("ix_sync_account_time", "social_account_id", "created_at"),)
