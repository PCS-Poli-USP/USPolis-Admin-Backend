"""Create intentional conflicts contraints

Revision ID: 557af0c2f159
Revises: a575f91e1e7d
Create Date: 2025-05-10 19:41:51.671503

"""

from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "557af0c2f159"
down_revision: str | None = "a575f91e1e7d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "intentionalconflict_second_occurrence_id_fkey",
        "intentionalconflict",
        type_="foreignkey",
    )
    op.drop_constraint(
        "intentionalconflict_first_occurrence_id_fkey",
        "intentionalconflict",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "intentionalconflict",
        "occurrence",
        ["second_occurrence_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None,
        "intentionalconflict",
        "occurrence",
        ["first_occurrence_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "intentionalconflict_first_occurrence_id_fkey",
        "intentionalconflict",
        type_="foreignkey",
    )
    op.drop_constraint(
        "intentionalconflict_second_occurrence_id_fkey",
        "intentionalconflict",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "intentionalconflict_fist_occurrence_id_fkey",
        "intentionalconflict",
        "occurrence",
        ["first_occurrence_id"],
        ["id"],
    )
    op.create_foreign_key(
        "intentionalconflict_second_occurrence_id_fkey",
        "intentionalconflict",
        "occurrence",
        ["second_occurrence_id"],
        ["id"],
    )
