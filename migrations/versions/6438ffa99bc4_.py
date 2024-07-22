"""empty message

Revision ID: 6438ffa99bc4
Revises: dd4033725348, f83c0dd3cfa4
Create Date: 2024-07-21 18:18:36.619956

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '6438ffa99bc4'
down_revision: Union[str, None] = ('dd4033725348', 'f83c0dd3cfa4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
