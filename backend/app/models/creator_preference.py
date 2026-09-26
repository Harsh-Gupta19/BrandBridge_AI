"""Database mapping for creator_preferences."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CreatorPreference(Base):
    __tablename__ = "creator_preferences"

    creator_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("creator_profiles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    accepted_categories: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    excluded_categories: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    excluded_brand_ids: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    preferred_models: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    min_rate_inr: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2), nullable=True)
    values_statement: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    content_restrictions: Mapped[list[str]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    max_campaigns_month: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    responds_within_hours: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
        onupdate=sa.func.now(),
    )
