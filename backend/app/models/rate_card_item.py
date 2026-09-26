"""Database mapping for rate_card_items."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import ContentType, Platform


class RateCardItem(Base):
    __tablename__ = "rate_card_items"

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
    content_type: Mapped[ContentType] = mapped_column(
        sa.Enum(ContentType, native_enum=False, length=16, validate_strings=True), nullable=False
    )
    rate_amount: Mapped[Decimal] = mapped_column(sa.Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        sa.CHAR(3), nullable=False, server_default=sa.text("'INR'")
    )
    is_negotiable: Mapped[bool] = mapped_column(
        sa.Boolean(), nullable=False, server_default=sa.text("true")
    )
    active: Mapped[bool] = mapped_column(
        sa.Boolean(), nullable=False, server_default=sa.text("true")
    )
    effective_from: Mapped[date] = mapped_column(
        sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")
    )
    effective_to: Mapped[date | None] = mapped_column(sa.Date(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    __table_args__ = (
        sa.CheckConstraint("rate_amount >= 0", name="ck_rate_amount_nonnegative"),
        sa.Index(
            "uq_rate_active",
            "creator_id",
            "platform",
            "content_type",
            unique=True,
            postgresql_where=sa.text("active = true"),
        ),
    )
