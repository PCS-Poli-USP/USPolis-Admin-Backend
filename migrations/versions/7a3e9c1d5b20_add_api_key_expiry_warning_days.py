"""add apikey.expiry_warning_days

Revision ID: 7a3e9c1d5b20
Revises: d4b7e2a91c50
Create Date: 2026-11-16 12:00:00.000000

Records which expiry warning email (30, 7 or 1 day before expires_at) was
already sent for a key, so the daily task never sends the same one twice,
even if it runs again after a restart or on more than one worker.

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a3e9c1d5b20"
down_revision: str | None = "d4b7e2a91c50"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "apikey", sa.Column("expiry_warning_days", sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("apikey", "expiry_warning_days")
