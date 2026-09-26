"""Database mapping for brand_profiles."""

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.user import User


class BrandProfile(TimestampMixin, Base):
    __tablename__ = "brand_profiles"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
    )
    brand_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    industry: Mapped[str | None] = mapped_column(sa.String(120), nullable=True)
    website_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)

    __table_args__ = (sa.UniqueConstraint("user_id"),)

    user: Mapped["User"] = relationship(back_populates="brand_profile")
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="brand_profile")
