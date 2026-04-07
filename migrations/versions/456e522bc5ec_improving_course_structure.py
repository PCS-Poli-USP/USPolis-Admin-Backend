"""improving course structure

Revision ID: 456e522bc5ec
Revises: f1df976650ac
Create Date: 2026-04-07 16:38:42.273016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '456e522bc5ec'
down_revision: Union[str, None] = 'f1df976650ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    category_enum = sa.Enum(
        "MANDATORY",
        "FREE_ELECTIVE",
        "TRACK_ELECTIVE",
        name="curriculum_subject_category"
    )
    category_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "curriculumsubject",
        sa.Column("category", category_enum, nullable=True)
    )
    # Define valor padrão para registros existentes
    op.execute("UPDATE curriculumsubject SET category = 'MANDATORY' WHERE category IS NULL")
    op.alter_column("curriculumsubject", "category", nullable=False)

def downgrade() -> None:
    op.drop_column("curriculumsubject", "category")

    category_enum = sa.Enum(
        "MANDATORY",
        "FREE_ELECTIVE",
        "TRACK_ELECTIVE",
        name="curriculum_subject_category"
    )

    category_enum.drop(op.get_bind(), checkfirst=True)
