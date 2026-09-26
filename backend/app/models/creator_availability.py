"""Database mapping for creator_availability."""

from datetime import date
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CreatorAvailability(Base):
    __tablename__ = "creator_availability"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    creator_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        sa.ForeignKey("creator_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    start_date: Mapped[date] = mapped_column(sa.Date(), nullable=False)
    end_date: Mapped[date] = mapped_column(sa.Date(), nullable=False)
    status: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, server_default=sa.text("'AVAILABLE'")
    )
    notes: Mapped[str | None] = mapped_column(sa.String(240), nullable=True)

    __table_args__ = (sa.CheckConstraint("end_date >= start_date", name="ck_availability_dates"),)
