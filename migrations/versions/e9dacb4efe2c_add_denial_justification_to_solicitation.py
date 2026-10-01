"""add denial justification to solicitation

Revision ID: e9dacb4efe2c
Revises: dffa01899ea5
Create Date: 2026-09-03 22:29:18.787601

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "e9dacb4efe2c"
down_revision: str | None = "dffa01899ea5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "solicitation",
        sa.Column(
            "denial_justification", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    # Denials before this column existed only ever recorded their reason in
    # the notification email - backfill a placeholder for already-denied
    # solicitations so the system doesn't show a blank reason for them.
    op.execute(
        """
        UPDATE solicitation
        SET denial_justification = 'Justificativa dada por email'
        FROM reservation
        WHERE reservation.id = solicitation.reservation_id
        AND reservation.status = 'DENIED'
        """
    )


def downgrade() -> None:
    op.drop_column("solicitation", "denial_justification")
