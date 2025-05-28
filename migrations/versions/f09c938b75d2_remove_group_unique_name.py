"""Remove group unique name

Revision ID: f09c938b75d2
Revises: 98e28ed3304b
Create Date: 2025-05-28 13:15:40.193400

"""

from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f09c938b75d2"
down_revision: str | None = "98e28ed3304b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("ix_group_name", table_name="group")


def downgrade() -> None:
    op.create_index("ix_group_name", "group", ["name"], unique=True)
