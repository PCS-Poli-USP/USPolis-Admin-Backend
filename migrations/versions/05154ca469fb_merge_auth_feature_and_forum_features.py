"""Merge auth-feature and forum features

Revision ID: 05154ca469fb
Revises: 4abbc03d3542, 64a70f848243
Create Date: 2024-11-29 02:20:58.666026

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '05154ca469fb'
down_revision: Union[str, None] = ('4abbc03d3542', '64a70f848243')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
