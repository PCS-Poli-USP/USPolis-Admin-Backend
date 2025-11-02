"""Make reservation childen unique

Revision ID: 978c086c9b43
Revises: 1c0017953ad7
Create Date: 2025-09-10 00:37:01.846397

"""

from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "978c086c9b43"
down_revision: str | None = "1c0017953ad7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# THAT IS A BREAKCHANGE MIGRATION, MAKE SURE TO NOT DOWNGRADE
# UNIQUE CONSTRAINTS ARE REQUIRED FOR DATA CONSISTENCY
# AND TO AVOID MULTIPLE CHILDREN FOR A SINGLE RESERVATION


def upgrade() -> None:
    # Not correct, is necessary to make the column unique
    # Maybe delete the most old entry when multiple entries exist

    op.create_unique_constraint("event_reservation_id_key", "event", ["reservation_id"])
    op.create_unique_constraint("exam_reservation_id_key", "exam", ["reservation_id"])
    op.create_unique_constraint(
        "meeting_reservation_id_key", "meeting", ["reservation_id"]
    )


def downgrade() -> None:
    op.drop_constraint("meeting_reservation_id_key", "meeting", type_="unique")
    op.drop_constraint("exam_reservation_id_key", "exam", type_="unique")
    op.drop_constraint("event_reservation_id_key", "event", type_="unique")
