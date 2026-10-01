"""Add building to resource enum

Revision ID: 6c1f6ef0b2a4
Revises: bc62ed983810
Create Date: 2026-06-02 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6c1f6ef0b2a4"
down_revision: str | None = "bc62ed983810"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE resource_enum ADD VALUE IF NOT EXISTS 'BUILDING'")


def downgrade() -> None:
    pass
