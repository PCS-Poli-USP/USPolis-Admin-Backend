"""Merge api status and role-based-permissions branches

Revision ID: dffa01899ea5
Revises: 2ea02fbd7b52, 6950bd048a6d
Create Date: 2026-08-24 21:39:34.923212

"""

from collections.abc import Sequence


# revision identifiers, used by Alembic.
revision: str = "dffa01899ea5"
down_revision: str | tuple[str, ...] | None = ("2ea02fbd7b52", "6950bd048a6d")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
