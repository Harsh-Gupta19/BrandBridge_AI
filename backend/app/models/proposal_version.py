"""Database mapping for proposal_versions."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import InitiatedBy


class ProposalVersion(Base):
    __tablename__ = "proposal_versions"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    proposal_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("proposals.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_no: Mapped[int] = mapped_column(sa.SmallInteger(), nullable=False)
    amount: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(
        sa.CHAR(3), nullable=False, server_default=sa.text("'INR'")
    )
    deliverables: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB(), nullable=False, server_default=sa.text("'[]'"), default=list
    )
    message: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)
    created_by_user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
    )
    created_by_role: Mapped[InitiatedBy] = mapped_column(
        sa.Enum(InitiatedBy, native_enum=False, length=8, validate_strings=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
    )

    __table_args__ = (sa.UniqueConstraint("proposal_id", "version_no", name="uq_proposal_version"),)
