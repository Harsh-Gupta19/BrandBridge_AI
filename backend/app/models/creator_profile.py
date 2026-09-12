from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class CreatorProfile(TimestampMixin, Base):
    __tablename__ = "creator_profiles"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    categories: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    audience_summary: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    user: Mapped["User"] = relationship(back_populates="creator_profile")
    proposals: Mapped[list["Proposal"]] = relationship(back_populates="creator_profile")
