"""Database mapping for eligibility_exclusions."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class EligibilityExclusion(Base):
    __tablename__ = "eligibility_exclusions"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    creator_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("creator_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    rule_code: Mapped[str] = mapped_column(sa.String(48), nullable=False)
    rule_version: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    detail: Mapped[str | None] = mapped_column(sa.String(240), nullable=True)
    confidence: Mapped[Decimal | None] = mapped_column(sa.Numeric(4, 3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
