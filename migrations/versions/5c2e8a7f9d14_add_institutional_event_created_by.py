"""add institutional event created_by

Revision ID: 5c2e8a7f9d14
Revises: 8d4f2b6e1a93
Create Date: 2026-11-22 12:00:00.000000

Records who created each institutional event, so only the creator or an admin
edits or deletes it (as holidays and calendars). Nullable: events created
before this migration have no creator, and only admins can change them.
Deleting the user keeps the event (SET NULL).

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5c2e8a7f9d14"
down_revision: str | None = "8d4f2b6e1a93"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "institutionalevent",
        sa.Column("created_by_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "institutionalevent_created_by_id_fkey",
        "institutionalevent",
        "user",
        ["created_by_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "institutionalevent_created_by_id_fkey",
        "institutionalevent",
        type_="foreignkey",
    )
    op.drop_column("institutionalevent", "created_by_id")
