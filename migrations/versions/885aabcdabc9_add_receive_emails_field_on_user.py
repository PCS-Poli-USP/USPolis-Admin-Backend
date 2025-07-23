"""Add receive_emails field on user

Revision ID: 885aabcdabc9
Revises: c03767cc42a7
Create Date: 2025-07-22 20:20:49.737962

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "885aabcdabc9"
down_revision: str | None = "c03767cc42a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("user", sa.Column("receive_emails", sa.Boolean(), nullable=True))
    op.execute(sa.text('UPDATE "user" SET receive_emails = TRUE'))
    op.alter_column("user", "receive_emails", nullable=False)


def downgrade() -> None:
    op.drop_column("user", "receive_emails")
