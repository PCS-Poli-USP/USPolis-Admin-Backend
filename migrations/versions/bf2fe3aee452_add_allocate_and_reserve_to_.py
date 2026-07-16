"""Add allocate and reserve to buildingaction enum

Revision ID: bf2fe3aee452
Revises: b5645a4b9a92
Create Date: 2026-07-15 20:58:57.059333

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bf2fe3aee452"
down_revision: str | None = "b5645a4b9a92"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The enum column stores the Python enum member *name* (e.g. "CREATE"), not
    # its value ("create") - matching every other value already in this type.
    op.execute("ALTER TYPE buildingaction ADD VALUE IF NOT EXISTS 'ALLOCATE'")
    op.execute("ALTER TYPE buildingaction ADD VALUE IF NOT EXISTS 'RESERVE'")


def downgrade() -> None:
    # Postgres has no "ALTER TYPE ... DROP VALUE", so the type has to be
    # recreated without ALLOCATE/RESERVE. Any existing grant using them can't
    # survive the downgrade: strip those two values from every actions array,
    # then drop any permission left with no actions at all.
    op.execute(
        "UPDATE buildingpermission "
        "SET actions = array_remove(array_remove(actions, 'ALLOCATE'), 'RESERVE') "
        "WHERE actions && ARRAY['ALLOCATE', 'RESERVE']::buildingaction[]"
    )
    op.execute("DELETE FROM buildingpermission WHERE actions = '{}'")

    op.execute("ALTER TYPE buildingaction RENAME TO buildingaction_old")
    op.execute("CREATE TYPE buildingaction AS ENUM ('CREATE', 'READ', 'UPDATE', 'DELETE')")
    op.execute(
        "ALTER TABLE buildingpermission "
        "ALTER COLUMN actions TYPE buildingaction[] "
        "USING actions::text[]::buildingaction[]"
    )
    op.execute("DROP TYPE buildingaction_old")
