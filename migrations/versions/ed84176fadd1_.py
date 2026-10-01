"""add request action to classroomaction

Revision ID: ed84176fadd1
Revises: e9dacb4efe2c
Create Date: 2026-09-05 17:16:13.941918

"""

from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "ed84176fadd1"
down_revision: str | None = "e9dacb4efe2c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE classroomaction ADD VALUE IF NOT EXISTS 'REQUEST'")


def downgrade() -> None:
    # Postgres has no DROP VALUE for enums - strip the value from every
    # actions array, delete any permission left with an empty actions list,
    # then recreate the type without it. Mirrors
    # bf2fe3aee452_add_allocate_and_reserve_to_.py's downgrade, retargeted at
    # classroompermission/classroomaction instead of
    # buildingpermission/buildingaction.
    op.execute(
        "UPDATE classroompermission "
        "SET actions = array_remove(actions, 'REQUEST') "
        "WHERE actions && ARRAY['REQUEST']::classroomaction[]"
    )
    op.execute("DELETE FROM classroompermission WHERE actions = '{}'")
    op.execute("ALTER TYPE classroomaction RENAME TO classroomaction_old")
    op.execute(
        "CREATE TYPE classroomaction AS ENUM "
        "('CREATE', 'READ', 'UPDATE', 'DELETE', 'ALLOCATE', 'RESERVE')"
    )
    op.execute(
        "ALTER TABLE classroompermission "
        "ALTER COLUMN actions TYPE classroomaction[] "
        "USING actions::text[]::classroomaction[]"
    )
    op.execute("DROP TYPE classroomaction_old")
