"""Database mapping for agreements."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Agreement(Base):
    __tablename__ = "agreements"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    collaboration_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("collaborations.id", ondelete="CASCADE"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(
        sa.SmallInteger(), nullable=False, server_default=sa.text("1")
    )
    draft_text: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    evidence_refs: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    generated_by: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, server_default=sa.text("'AI_DRAFT'")
    )
    status: Mapped[str] = mapped_column(
        sa.String(20), nullable=False, server_default=sa.text("'DRAFT'")
    )
    brand_approved_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    creator_approved_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
