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
    bind = op.get_bind()

    op.create_table(
        "exam",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reservation_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=True),
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
        sa.Column("link", sqlmodel.sql.sqltypes.AutoString(), nullable=True),  # pyright: ignore[reportAttributeAccessIssue]
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
        sa.Column("link", sqlmodel.sql.sqltypes.AutoString(), nullable=True),  # pyright: ignore[reportAttributeAccessIssue]
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

    # Deixa tudo por padrão como "EVENT"
    op.execute("UPDATE reservation SET type = 'EVENT';")
    op.execute("UPDATE classroomsolicitation SET reservation_type = 'EVENT';")
    new_reservation_type = sa.Enum(
        "EXAM", "MEETING", "EVENT", name="newreservationtype"
    )
    new_reservation_type.create(bind, checkfirst=True)
    op.execute("""
        ALTER TABLE reservation 
        ALTER COLUMN type 
        TYPE newreservationtype 
        USING type::text::newreservationtype;
    """)
    op.execute("""
        ALTER TABLE classroomsolicitation 
        ALTER COLUMN reservation_type 
        TYPE newreservationtype 
        USING reservation_type::text::newreservationtype;
    """)
    op.execute("DROP TYPE reservationtype;")
    op.execute("ALTER TYPE newreservationtype RENAME TO reservationtype;")

    # Seleciona todas as reservas e cria para ela eventos (valor padrão agora)
    rows = bind.execute(sa.text("""SELECT * FROM reservation;""")).fetchall()
    # row = (id, title, type, reason, updated_at, created_by_id, classroom_id)

    # Cria um evento para cada reserva
    for row in rows:
        bind.execute(
            sa.text("""
                INSERT INTO reservationevent (reservation_id, link, type)
                VALUES (:rid, NULL, :etype)
            """),
            {"rid": row[0], "etype": "OTHER"},
        )
    print("Reservations updated:", len(rows))


def downgrade() -> None:
    old_reservation_type = sa.Enum(
        "EXAM", "MEETING", "EVENT", "OTHER", name="oldreservationtype"
    )
    old_reservation_type.create(op.get_bind(), checkfirst=True)

    op.execute("""
        ALTER TABLE reservation 
        ALTER COLUMN type 
        TYPE oldreservationtype 
        USING type::text::oldreservationtype;
    """)
    op.execute("""
        ALTER TABLE classroomsolicitation 
        ALTER COLUMN reservation_type 
        TYPE oldreservationtype 
        USING reservation_type::text::oldreservationtype;
    """)
    op.execute("DROP TYPE reservationtype;")
    op.execute("ALTER TYPE oldreservationtype RENAME TO reservationtype;")

    op.drop_column("reservation", "audiovisual")
    op.drop_table("reservationevent")
    op.execute("DROP TYPE public.eventtype")
    op.drop_table("meeting")
    op.drop_table("exam")
