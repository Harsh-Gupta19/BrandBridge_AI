"""Activate multiple roles per account, preserving existing users.

Build Manual section 5.2.
"""

import sqlalchemy as sa

from alembic import op

revision = "0002_dual_role_identity"
down_revision = "0001_initial_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_roles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("CREATOR", "BRAND", "ADMIN", name="user_role", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "activated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role", name="uq_user_role"),
    )
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"], unique=False)
    op.add_column(
        "users",
        sa.Column(
            "status", sa.String(length=20), server_default=sa.text("'ACTIVE'"), nullable=False
        ),
    )
    op.execute(
        """
        UPDATE users SET status = CASE WHEN is_active THEN 'ACTIVE' ELSE 'INACTIVE' END
        """
    )
    op.execute(
        """
        INSERT INTO user_roles (id, user_id, role, activated_at)
        SELECT gen_random_uuid(), id, role, created_at FROM users
        """
    )
    op.drop_column("users", "role")


def downgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
         IF EXISTS (SELECT 1 FROM users u LEFT JOIN user_roles r ON r.user_id = u.id
                    GROUP BY u.id HAVING count(r.id) <> 1) THEN
           RAISE EXCEPTION 'Cannot downgrade dual-role identity: %',
               'every user must have exactly one role';
         END IF;
         END $$
        """
    )
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("CREATOR", "BRAND", "ADMIN", name="user_role", native_enum=False),
            nullable=True,
        ),
    )
    op.execute(
        """
        UPDATE users u SET role = r.role FROM user_roles r WHERE r.user_id = u.id
        """
    )
    op.alter_column(
        "users",
        "role",
        existing_type=sa.Enum("CREATOR", "BRAND", "ADMIN", name="user_role", native_enum=False),
        nullable=False,
    )
    op.execute(
        """
        UPDATE users SET is_active = (status = 'ACTIVE')
        """
    )
    op.drop_column("users", "status")
    op.drop_index("ix_user_roles_user_id", table_name="user_roles")
    op.drop_table("user_roles")
