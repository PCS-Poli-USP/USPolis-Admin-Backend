"""Merge auth-feature and forum features

Revision ID: 05154ca469fb
Revises: 4abbc03d3542, 64a70f848243
Create Date: 2024-11-29 02:20:58.666026

"""

from collections.abc import Sequence


# revision identifiers, used by Alembic.
revision: str = "05154ca469fb"
down_revision: str | None = ("4abbc03d3542", "64a70f848243")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
