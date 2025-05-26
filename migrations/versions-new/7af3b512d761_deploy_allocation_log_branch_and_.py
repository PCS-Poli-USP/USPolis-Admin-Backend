"""Deploy allocation log branch and deleted by in solicitation

Revision ID: 7af3b512d761
Revises: 3a1eb5622840, 78a13f742e39
Create Date: 2025-03-23 19:50:50.893528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '7af3b512d761'
down_revision: Union[str, None] = ('3a1eb5622840', '78a13f742e39')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
