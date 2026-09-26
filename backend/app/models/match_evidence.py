"""Database mapping for match_evidence."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import DataProvenance


class MatchEvidence(Base):
    __tablename__ = "match_evidence"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    match_score_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("match_scores.id", ondelete="CASCADE"),
        nullable=False,
    )
    kind: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    label: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    value_text: Mapped[str | None] = mapped_column(sa.String(240), nullable=True)
    value_numeric: Mapped[Decimal | None] = mapped_column(sa.Numeric(14, 4), nullable=True)
    provenance: Mapped[DataProvenance | None] = mapped_column(
        sa.Enum(DataProvenance, native_enum=False, length=24, validate_strings=True), nullable=True
    )
    captured_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
