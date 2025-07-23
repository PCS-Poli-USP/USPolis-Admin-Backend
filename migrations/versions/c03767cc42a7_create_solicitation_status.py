"""Create solicitation status

Revision ID: c03767cc42a7
Revises: 5c09edeeacb7
Create Date: 2025-06-29 09:37:36.425268

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c03767cc42a7"
down_revision: str | None = "5c09edeeacb7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    status_type = sa.Enum(
        "PENDING",
        "APPROVED",
        "DENIED",
        "CANCELLED",
        "DELETED",
        name="solicitationstatus",
    )
    status_type.create(op.get_bind(), checkfirst=False)

    op.add_column(
        "classroomsolicitation",
        sa.Column(
            "status",
            status_type,
            nullable=True,
        ),
    )

    # Make sure that deleted is check first, because you can have a solicitation that was initially approved, then deleted.
    op.execute("""
        UPDATE classroomsolicitation
        SET status = CASE
            WHEN deleted = TRUE THEN 'DELETED'::solicitationstatus
            WHEN approved = TRUE THEN 'APPROVED'::solicitationstatus
            WHEN denied = TRUE THEN 'DENIED'::solicitationstatus
            ELSE 'PENDING'
        END
    """)
    op.alter_column(
        "classroomsolicitation",
        "status",
        existing_type=status_type,
        nullable=False,
    )

    op.drop_column("classroomsolicitation", "approved")
    op.drop_column("classroomsolicitation", "denied")
    op.drop_column("classroomsolicitation", "deleted")
    op.drop_column("classroomsolicitation", "closed")


def downgrade() -> None:
    op.add_column(
        "classroomsolicitation",
        sa.Column(
            "deleted", sa.BOOLEAN(), autoincrement=False, nullable=True, default=False
        ),
    )
    op.add_column(
        "classroomsolicitation",
        sa.Column(
            "denied", sa.BOOLEAN(), autoincrement=False, nullable=True, default=False
        ),
    )
    op.add_column(
        "classroomsolicitation",
        sa.Column(
            "approved", sa.BOOLEAN(), autoincrement=False, nullable=True, default=False
        ),
    )
    op.add_column(
        "classroomsolicitation",
        sa.Column(
            "closed", sa.BOOLEAN(), autoincrement=False, nullable=True, default=False
        ),
    )
    op.execute("""
        UPDATE classroomsolicitation
        SET deleted = CASE
            WHEN status = 'DELETED'::solicitationstatus THEN TRUE
            ELSE FALSE
        END
    """)
    op.execute("""
        UPDATE classroomsolicitation
        SET denied = CASE
            WHEN status = 'DENIED'::solicitationstatus THEN TRUE
            ELSE FALSE
        END
    """)
    op.execute("""
        UPDATE classroomsolicitation
        SET approved = CASE
            WHEN status = 'APPROVED'::solicitationstatus THEN TRUE
            ELSE FALSE
        END
    """)
    op.execute("""
        UPDATE classroomsolicitation
        SET closed = CASE
            WHEN status = 'CANCELLED'::solicitationstatus THEN TRUE
            WHEN status = 'DELETED'::solicitationstatus  THEN TRUE
            WHEN status = 'DENIED'::solicitationstatus  THEN TRUE
            WHEN status = 'APPROVED'::solicitationstatus  THEN TRUE
            ELSE FALSE
        END
    """)

    op.drop_column("classroomsolicitation", "status")
    op.execute("DROP TYPE public.solicitationstatus")

    op.alter_column(
        "classroomsolicitation",
        "deleted",
        existing_type=sa.BOOLEAN(),
        nullable=False,
    )
    op.alter_column(
        "classroomsolicitation",
        "denied",
        existing_type=sa.BOOLEAN(),
        nullable=False,
    )
    op.alter_column(
        "classroomsolicitation",
        "approved",
        existing_type=sa.BOOLEAN(),
        nullable=False,
    )
    op.alter_column(
        "classroomsolicitation",
        "closed",
        existing_type=sa.BOOLEAN(),
        nullable=False,
    )
