"""Database mapping for collaborations."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import CollaborationStatus


class Collaboration(Base):
    __tablename__ = "collaborations"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    accepted_proposal_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("proposals.id"), nullable=False
    )
    campaign_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("campaigns.id"), nullable=False
    )
    creator_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("creator_profiles.id"), nullable=False
    )
    brand_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("brand_profiles.id"), nullable=False
    )
    status: Mapped[CollaborationStatus] = mapped_column(
        sa.Enum(CollaborationStatus, native_enum=False, length=20, validate_strings=True),
        nullable=False,
        server_default=sa.text("'ACTIVE'"),
    )
    agreed_amount: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(
        sa.CHAR(3), nullable=False, server_default=sa.text("'INR'")
    )
    starts_on: Mapped[date | None] = mapped_column(sa.Date(), nullable=True)
    ends_on: Mapped[date | None] = mapped_column(sa.Date(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    __table_args__ = (
        sa.UniqueConstraint("accepted_proposal_id", name="uq_collaboration_accepted_proposal"),
    )
