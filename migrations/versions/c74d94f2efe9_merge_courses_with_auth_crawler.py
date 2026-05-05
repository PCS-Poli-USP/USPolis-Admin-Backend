"""merge courses with auth crawler

Revision ID: c74d94f2efe9
Revises: 456e522bc5ec, 61c169cfae42
Create Date: 2026-05-05 20:28:10.100851

"""

from collections.abc import Sequence


# revision identifiers, used by Alembic.
revision: str = "c74d94f2efe9"
down_revision: str | None | tuple[str, str] = ("456e522bc5ec", "61c169cfae42")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
