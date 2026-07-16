"""Merge curriculum and role-permissions branches

Revision ID: b5645a4b9a92
Revises: 5e270fe67556, d477d8a96afa
Create Date: 2026-07-15 20:00:46.157003

"""

from collections.abc import Sequence


# revision identifiers, used by Alembic.
revision: str = "b5645a4b9a92"
down_revision: str | tuple[str, ...] | None = ("5e270fe67556", "d477d8a96afa")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
