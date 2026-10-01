"""rename classroom remote to restricted

Revision ID: 299a3408e676
Revises: ed84176fadd1
Create Date: 2026-09-05 18:24:12.443910

"""

from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "299a3408e676"
down_revision: str | None = "ed84176fadd1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("classroom", "remote", new_column_name="restricted")


def downgrade() -> None:
    op.alter_column("classroom", "restricted", new_column_name="remote")
