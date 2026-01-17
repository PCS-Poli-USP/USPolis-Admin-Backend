"""Classroom permission feature

Revision ID: 5be61781ecc0
Revises: b8d765aeee27
Create Date: 2026-01-15 20:47:59.781739

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5be61781ecc0"
down_revision: str | None = "b8d765aeee27"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

permission_enum = postgresql.ENUM(
    "VIEW",
    "RESERVE",
    name="classroom_permission_type_enum",
)


def upgrade() -> None:
    op.create_table(
        "classroompermission",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("classroom_id", sa.Integer(), nullable=False),
        sa.Column("given_by_id", sa.Integer(), nullable=False),
        sa.Column(
            "permissions",
            postgresql.ARRAY(permission_enum),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "cardinality(permissions) > 0", name="ck_permissions_not_empty"
        ),
        sa.ForeignKeyConstraint(
            ["classroom_id"],
            ["classroom.id"],
        ),
        sa.ForeignKeyConstraint(
            ["given_by_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "classroom_id", name="unique_classroom_permission_per_user"
        ),
    )
    op.add_column("classroom", sa.Column("restricted", sa.Boolean(), nullable=True))
    op.execute("""UPDATE classroom SET restricted = false WHERE restricted IS NULL;""")
    op.alter_column(
        "classroom",
        "restricted",
        nullable=False,
    )

    op.add_column("classroom", sa.Column("laboratory", sa.Boolean(), nullable=True))
    op.execute("""UPDATE classroom SET laboratory = false WHERE laboratory IS NULL;""")
    op.alter_column(
        "classroom",
        "laboratory",
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("classroom", "laboratory")
    op.drop_column("classroom", "restricted")
    op.drop_table("classroompermission")

    permission_enum.drop(op.get_bind(), checkfirst=True)
