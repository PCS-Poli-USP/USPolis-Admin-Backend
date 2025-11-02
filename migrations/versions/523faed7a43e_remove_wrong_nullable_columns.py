"""Remove wrong nullable columns

Revision ID: 523faed7a43e
Revises: f09c938b75d2
Create Date: 2025-05-31 21:00:11.941388

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "523faed7a43e"
down_revision: str | None = "f09c938b75d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "building_main_group_id_key", "building", ["main_group_id"]
    )
    op.alter_column(
        "calendar", "created_by_id", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "class",
        "professors",
        existing_type=postgresql.ARRAY(sa.VARCHAR()),
        nullable=False,
    )
    op.alter_column(
        "classroomsolicitation",
        "dates",
        existing_type=postgresql.ARRAY(sa.DATE()),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "classroomsolicitation",
        "dates",
        existing_type=postgresql.ARRAY(sa.DATE()),
        nullable=True,
    )
    op.alter_column(
        "class",
        "professors",
        existing_type=postgresql.ARRAY(sa.VARCHAR()),
        nullable=True,
    )
    op.alter_column(
        "calendar", "created_by_id", existing_type=sa.INTEGER(), nullable=True
    )
    op.drop_constraint("building_main_group_id_key", "building", type_="unique")
