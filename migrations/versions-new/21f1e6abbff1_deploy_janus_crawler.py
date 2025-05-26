"""Deploy Janus Crawler

Revision ID: 21f1e6abbff1
Revises: 7af3b512d761, d41e4f7ca46f
Create Date: 2025-04-03 05:10:12.009777

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '21f1e6abbff1'
down_revision: Union[str, None] = ('7af3b512d761', 'd41e4f7ca46f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
