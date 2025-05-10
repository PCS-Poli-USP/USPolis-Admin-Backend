"""Intentional Conflict table

Revision ID: a575f91e1e7d
Revises: abcd4d03111f
Create Date: 2025-05-10 18:37:22.392146

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a575f91e1e7d"
down_revision: str | None = "abcd4d03111f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "intentionalconflict",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fist_occurrence_id", sa.Integer(), nullable=False),
        sa.Column("second_occurrence_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["fist_occurrence_id"],
            ["occurrence.id"],
        ),
        sa.ForeignKeyConstraint(
            ["second_occurrence_id"],
            ["occurrence.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "fist_occurrence_id",
            "second_occurrence_id",
            name="unique_occurrence_pair",
        ),
    )


def downgrade() -> None:
    op.drop_table("conflict")
