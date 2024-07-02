"""Add month week as enum on schedule

Revision ID: ce51866da32d
Revises: d82d2bacee2d
Create Date: 2024-07-01 01:08:45.742362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'ce51866da32d'
down_revision: Union[str, None] = 'd82d2bacee2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

monthweek_enum = sa.Enum('FIRST', 'SECOND', 'THIRD', 'LAST', name='monthweek')


def upgrade() -> None:
    # Crie o tipo ENUM no banco de dados
    monthweek_enum.create(op.get_bind(), checkfirst=True)

    # Altere a coluna para usar o novo tipo ENUM, especificando o USING
    op.alter_column('schedule', 'month_week',
                    existing_type=sa.Integer(),
                    type_=monthweek_enum,
                    existing_nullable=True,
                    postgresql_using='month_week::text::monthweek')


def downgrade() -> None:
    # Altere a coluna de volta para seu tipo original (neste caso, INTEGER)
    op.alter_column('schedule', 'month_week',
                    existing_type=monthweek_enum,
                    type_=sa.Integer(),
                    existing_nullable=True,
                    postgresql_using='month_week::monthweek::integer')
    
    # Remova o tipo ENUM do banco de dados
    monthweek_enum.drop(op.get_bind(), checkfirst=True)
