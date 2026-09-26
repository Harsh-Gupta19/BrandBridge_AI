"""Database mapping for collaboration_outcomes."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CollaborationOutcome(Base):
    __tablename__ = "collaboration_outcomes"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    proposal_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("proposals.id", ondelete="CASCADE"),
        nullable=False,
    )
    accepted: Mapped[bool | None] = mapped_column(sa.Boolean(), nullable=True)
    completed: Mapped[bool | None] = mapped_column(sa.Boolean(), nullable=True)
    brand_rating: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    creator_rating: Mapped[int | None] = mapped_column(sa.SmallInteger(), nullable=True)
    outcome_metrics: Mapped[dict[str, Any]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'{}'"), default=dict
    )
    recorded_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    __table_args__ = (sa.UniqueConstraint("proposal_id", name="uq_outcome_proposal"),)
