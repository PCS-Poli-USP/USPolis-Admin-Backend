"""Allow null resource_id in permissions

Revision ID: c8c2b1d4f0a1
Revises: aed010156c3c
Create Date: 2026-05-27 22:19:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c8c2b1d4f0a1"
down_revision: str | None = "aed010156c3c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE classroompermission DROP CONSTRAINT IF EXISTS permission_check_user_or_role"
    )
    op.execute(
        "ALTER TABLE coursepermission DROP CONSTRAINT IF EXISTS permission_check_user_or_role"
    )
    op.create_check_constraint(
        "permission_check_user_or_role",
        "classroompermission",
        "user_id IS NOT NULL OR role_id IS NOT NULL",
    )
    op.create_check_constraint(
        "permission_check_user_or_role",
        "coursepermission",
        "user_id IS NOT NULL OR role_id IS NOT NULL",
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE classroompermission DROP CONSTRAINT IF EXISTS permission_check_user_or_role"
    )
    op.execute(
        "ALTER TABLE coursepermission DROP CONSTRAINT IF EXISTS permission_check_user_or_role"
    )
    op.create_check_constraint(
        "permission_check_user_or_role",
        "classroompermission",
        "classroom_id IS NOT NULL",
    )
    op.create_check_constraint(
        "permission_check_user_or_role",
        "coursepermission",
        "course_id IS NOT NULL",
    )
