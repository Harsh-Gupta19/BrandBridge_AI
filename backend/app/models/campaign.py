from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Campaign(TimestampMixin, Base):
    __tablename__ = "campaigns"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    brand_profile_id: Mapped[UUID] = mapped_column(ForeignKey("brand_profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    brief: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    target_country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    target_audience: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    preferred_platforms: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    creator_categories: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    content_formats: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    brand_profile: Mapped["BrandProfile"] = relationship(back_populates="campaigns")
    proposals: Mapped[list["Proposal"]] = relationship(back_populates="campaign")
