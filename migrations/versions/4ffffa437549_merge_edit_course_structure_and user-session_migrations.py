"""merge edit course structure and user-session migrations

Revision ID: 4ffffa437549
Revises: 8e2d0a854903, b8d765aeee27
Create Date: 2026-02-15 19:57:26.851335

"""

from collections.abc import Sequence


# revision identifiers, used by Alembic.
revision: str = "4ffffa437549"
down_revision: str | None = ("8e2d0a854903", "b8d765aeee27")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
