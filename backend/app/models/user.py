"""Database mapping for users."""

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.brand_profile import BrandProfile
    from app.models.creator_profile import CreatorProfile
    from app.models.user_role import UserRoleRow


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    email: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean(), nullable=False, server_default=sa.text("true")
    )
    status: Mapped[str] = mapped_column(
        sa.String(20), nullable=False, server_default=sa.text("'ACTIVE'")
    )

    __table_args__ = (sa.UniqueConstraint("email"),)

    roles: Mapped[list["UserRoleRow"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    creator_profile: Mapped["CreatorProfile | None"] = relationship(back_populates="user")
    brand_profile: Mapped["BrandProfile | None"] = relationship(back_populates="user")

    def has_role(self, role: UserRole) -> bool:
        """Check activated membership; active-mode authorization belongs in dependencies."""
        return any(membership.role == role for membership in self.roles)
