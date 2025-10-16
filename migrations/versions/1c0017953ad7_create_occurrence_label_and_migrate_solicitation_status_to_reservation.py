"""Create occurrence label and migrate solicitation status to reservation

Revision ID: 1c0017953ad7
Revises: 0665bcbe2878
Create Date: 2025-09-03 20:47:42.435338

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "1c0017953ad7"
down_revision: str | None = "0665bcbe2878"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

old_status_type = sa.Enum(
    "PENDING",
    "APPROVED",
    "DENIED",
    "CANCELLED",
    "DELETED",
    name="solicitationstatus",
)

new_status_type = sa.Enum(
    "PENDING",
    "APPROVED",
    "DENIED",
    "CANCELLED",
    "DELETED",
    name="reservationstatus",
)


def upgrade() -> None:
    # Create OccurrenceLabel table
    op.create_table(
        "occurrencelabel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("occurrence_id", sa.Integer(), nullable=False),
        sa.Column("label", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["occurrence_id"],
            ["occurrence.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("occurrence_id"),
    )

    # Status migration from solicitation to reservation
    op.execute("ALTER TYPE public.solicitationstatus RENAME TO reservationstatus;")
    op.add_column(
        "reservation",
        sa.Column("status", new_status_type, nullable=True),
    )
    # Make solicitation status nullable first to avoid issues with existing data
    op.alter_column(
        "solicitation", "status", existing_type=new_status_type, nullable=True
    )

    # Copy status from solicitation to reservation
    op.execute("""
        UPDATE reservation
        SET status = solicitation.status
        FROM solicitation
        WHERE solicitation.reservation_id = reservation.id
    """)

    # Set any reservation without solicitation to APPROVED (for backward compatibility)
    op.execute("UPDATE reservation set status = 'APPROVED' WHERE status IS NULL;")

    op.alter_column(
        "reservation",
        "status",
        existing_type=new_status_type,
        nullable=False,
    )
    op.drop_column("solicitation", "status")


def downgrade() -> None:
    op.drop_table("occurrencelabel")

    # Status migration from reservation to solicitation
    op.execute("ALTER TYPE public.reservationstatus RENAME TO solicitationstatus;")
    op.add_column(
        "solicitation",
        sa.Column("status", old_status_type, nullable=True),
    )
    # Make reservation status nullable first to avoid issues with existing data
    op.alter_column(
        "reservation", "status", existing_type=old_status_type, nullable=True
    )

    # Copy status from solicitation to reservation
    op.execute("""
        UPDATE solicitation
        SET status = reservation.status
        FROM reservation
        WHERE reservation.id = solicitation.reservation_id
    """)

    op.alter_column(
        "solicitation",
        "status",
        existing_type=old_status_type,
        nullable=False,
    )
    op.drop_column("reservation", "status")
