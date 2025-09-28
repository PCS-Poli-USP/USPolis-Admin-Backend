"""deploy_remove_group_unique_name

Revision ID: b900ec39608c
Revises: 170b1b4806d4, f09c938b75d2
Create Date: 2025-05-28 16:31:12.552640

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b900ec39608c'
down_revision: Union[str, None] = ('170b1b4806d4', 'f09c938b75d2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
