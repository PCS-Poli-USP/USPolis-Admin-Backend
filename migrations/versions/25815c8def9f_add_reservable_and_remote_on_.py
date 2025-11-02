"""Add reservable and remote on classrooms

Revision ID: 25815c8def9f
Revises: 885aabcdabc9
Create Date: 2025-07-25 19:52:17.405391

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "25815c8def9f"
down_revision: str | None = "885aabcdabc9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("building_main_group_id_key", "building", type_="unique")
    op.add_column("classroom", sa.Column("reservable", sa.Boolean(), nullable=True))
    op.execute("UPDATE classroom SET reservable = TRUE")
    op.add_column("classroom", sa.Column("remote", sa.Boolean(), nullable=True))
    op.execute("UPDATE classroom SET remote = FALSE")
    op.alter_column("classroom", "reservable", nullable=False)
    op.alter_column("classroom", "remote", nullable=False)


def downgrade() -> None:
    op.drop_column("classroom", "remote")
    op.drop_column("classroom", "reservable")
    op.create_unique_constraint(
        "building_main_group_id_key", "building", ["main_group_id"]
    )
