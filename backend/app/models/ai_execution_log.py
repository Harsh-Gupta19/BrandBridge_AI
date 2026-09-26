"""Database mapping for ai_execution_logs."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AIExecutionLog(Base):
    __tablename__ = "ai_execution_logs"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    workflow_type: Mapped[str] = mapped_column(sa.String(40), nullable=False)
    subject_type: Mapped[str | None] = mapped_column(sa.String(24), nullable=True)
    subject_id: Mapped[UUID | None] = mapped_column(PostgresUUID(as_uuid=True), nullable=True)
    actor_user_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True
    )
    provider: Mapped[str | None] = mapped_column(sa.String(40), nullable=True)
    model: Mapped[str | None] = mapped_column(sa.String(80), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    state_version: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(sa.Integer(), nullable=True)
    estimated_cost: Mapped[Decimal | None] = mapped_column(sa.Numeric(10, 5), nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(sa.Integer(), nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(sa.Integer(), nullable=True)
    status: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    error_category: Mapped[str | None] = mapped_column(sa.String(40), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )
