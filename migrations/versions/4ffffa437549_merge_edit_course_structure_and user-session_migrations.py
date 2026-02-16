"""merge edit course structure and user-session migrations

Revision ID: 4ffffa437549
Revises: 8e2d0a854903, b8d765aeee27
Create Date: 2026-02-15 19:57:26.851335

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "4ffffa437549"
down_revision: Union[str, None] = ("8e2d0a854903", "b8d765aeee27")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
