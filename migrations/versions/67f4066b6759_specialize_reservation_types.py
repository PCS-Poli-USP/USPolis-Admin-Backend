"""specialize reservation types

Revision ID: 67f4066b6759
Revises: 760f7be15405
Create Date: 2025-08-16 22:04:11.824538

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "67f4066b6759"
down_revision: str | None = "760f7be15405"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "exam",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reservation_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["class_id"],
            ["class.id"],
        ),
        sa.ForeignKeyConstraint(
            ["reservation_id"],
            ["reservation.id"],
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subject.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "meeting",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reservation_id", sa.Integer(), nullable=False),
        sa.Column("link", sqlmodel.sql.sqltypes.AutoString(), nullable=True),  # type: ignore
        sa.ForeignKeyConstraint(
            ["reservation_id"],
            ["reservation.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    event_type = sa.Enum(
        "TALK", "WORKSHOP", "SELECTION_PROCESS", "OTHER", name="eventtype"
    )
    op.create_table(
        "reservationevent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reservation_id", sa.Integer(), nullable=False),
        sa.Column("link", sqlmodel.sql.sqltypes.AutoString(), nullable=True),  # type: ignore
        sa.Column(
            "type",
            type_=event_type,
            server_default="OTHER",
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["reservation_id"],
            ["reservation.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    audiovisual_enum = sa.Enum(
        "TV",
        "PROJECTOR",
        "NONE",
        name="audiovisualtype",
        schema="public",
        create_type=False,
    )
    op.add_column(
        "reservation",
        sa.Column(
            "audiovisual",
            audiovisual_enum,
            nullable=False,
            server_default="NONE",
        ),
    )


def downgrade() -> None:
    op.drop_column("reservation", "audiovisual")
    op.drop_table("reservationevent")
    op.execute("DROP TYPE public.eventtype")
    op.drop_table("meeting")
    op.drop_table("exam")
