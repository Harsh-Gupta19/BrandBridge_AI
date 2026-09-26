"""Database mapping for messages."""

from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    collaboration_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("collaborations.id", ondelete="CASCADE"),
        nullable=True,
    )
    proposal_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("proposals.id", ondelete="CASCADE"), nullable=True
    )
    sender_user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
    )
    body: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    __table_args__ = (
        sa.CheckConstraint(
            "collaboration_id IS NOT NULL OR proposal_id IS NOT NULL", name="ck_message_context"
        ),
    )
