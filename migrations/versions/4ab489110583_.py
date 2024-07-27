"""empty message

Revision ID: 4ab489110583
Revises: 9b72c7299a5e, dd138282c511
Create Date: 2024-07-27 15:44:35.868580

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '4ab489110583'
down_revision: Union[str, None] = ('9b72c7299a5e', 'dd138282c511')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
