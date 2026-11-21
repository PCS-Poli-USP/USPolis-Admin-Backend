"""backfill meeting rows for MEETING reservations without one

Revision ID: 3b9d7e5a1c24
Revises: 5c8e1f2a9b47
Create Date: 2026-11-20 18:00:00.000000

Every reservation must have exactly one child row matching its type (exam,
event or meeting), which specializes it. Until commit 7df2f93 (2025-11-02,
"fix solicitation create not creating the reservation children"), creating a
solicitation did not create the child. Nine MEETING reservations created that
day (ids 750-758, all cancelled/denied/deleted) were left without a meeting row.
EXAM and EVENT reservations are consistent.

A meeting row has no required data besides the reservation (link is nullable),
so the missing rows can be created safely. Exams could not be backfilled this
way (they need a subject), but none is missing.

"""

from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3b9d7e5a1c24"
down_revision: str | None = "5c8e1f2a9b47"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO meeting (reservation_id, link)
        SELECT r.id, NULL
        FROM reservation r
        LEFT JOIN meeting m ON m.reservation_id = r.id
        WHERE r.type = 'MEETING' AND m.id IS NULL
        """
    )


def downgrade() -> None:
    # Data fix: the backfilled rows are indistinguishable from valid ones and
    # removing them would break the reservation/child invariant again.
    pass
