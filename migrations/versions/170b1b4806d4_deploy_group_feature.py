"""Deploy group feature  26-05-2025

Revision ID: 170b1b4806d4
Revises: 21f1e6abbff1, 98e28ed3304b
Create Date: 2025-05-26 02:58:39.767209

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '170b1b4806d4'
down_revision: Union[str, None] = ('21f1e6abbff1', '98e28ed3304b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
