"""Update exam model and solicitation refactoring

Revision ID: 0665bcbe2878
Revises: 67f4066b6759
Create Date: 2025-08-22 19:22:47.714752

"""

from collections.abc import Sequence

from alembic import op
from pydantic import BaseModel
import sqlalchemy as sa
from datetime import time, date, datetime

from server.config import CONFIG


from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.reservation_type import ReservationType
from server.utils.enums.solicitation_status import SolicitationStatus

# revision identifiers, used by Alembic.
revision: str = "0665bcbe2878"
down_revision: str | None = "67f4066b6759"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


class ClassroomSolicitationSchema(BaseModel):
    id: int
    reservation_title: str
    reservation_type: ReservationType
    capacity: int
    start_time: time | None
    end_time: time | None
    dates: list[date]
    reason: str
    status: SolicitationStatus
    closed_by: str | None
    deleted_by: str | None
    created_at: datetime
    updated_at: datetime
    user_id: int
    building_id: int
    classroom_id: int | None
    reservation_id: int | None


def upgrade() -> None:
    bind = op.get_bind()

    op.rename_table("reservationevent", "event")
    op.drop_constraint(
        "reservationevent_reservation_id_fkey", "event", type_="foreignkey"
    )
    op.create_foreign_key(
        "event_reservation_id_fkey", "event", "reservation", ["reservation_id"], ["id"]
    )

    admin_id = bind.execute(
        sa.text("""
            SELECT id FROM "user" WHERE email = :email LIMIT 1
        """),
        {"email": CONFIG.first_superuser_email},
    ).scalar()
    if not admin_id:
        raise Exception(f"No {CONFIG.first_superuser_email} admin user found")

    # --- Reservation migration ---

    op.drop_constraint(
        "reservation_classroom_id_fkey", "reservation", type_="foreignkey"
    )
    op.drop_column("reservation", "classroom_id")

    # --- Solicitation migration ---
    # Rename FKS
    op.execute(
        sa.text(
            """ALTER TABLE public."classroomsolicitation" RENAME CONSTRAINT classroomsolicitation_building_id_fkey TO solicitation_building_id_fkey;"""
        )
    )
    op.execute(
        sa.text(
            """ALTER TABLE public."classroomsolicitation" RENAME CONSTRAINT classroomsolicitation_classroom_id_fkey TO solicitation_solicited_classroom_id_fkey;"""
        )
    )
    op.execute(
        sa.text(
            """ALTER TABLE public."classroomsolicitation" RENAME CONSTRAINT classroomsolicitation_user_id_fkey TO solicitation_user_id_fkey;"""
        )
    )
    op.execute(
        sa.text(
            """ALTER TABLE public."classroomsolicitation" RENAME CONSTRAINT classroomsolicitation_reservation_id_fkey TO solicitation_reservation_id_fkey;"""
        )
    )

    op.rename_table("classroomsolicitation", "solicitation")

    # Rename Constraints
    op.execute(
        sa.text(
            "ALTER TABLE solicitation RENAME COLUMN classroom_id TO solicited_classroom_id"
        )
    )

    op.create_check_constraint(
        "check_required_classroom_with_solicited_classroom_id_not_null",
        "solicitation",
        sa.text("(solicited_classroom_id IS NOT NULL) OR (required_classroom = FALSE)"),
    )

    op.drop_constraint(
        "check_required_classroom_with_classroom_id_not_null",
        "solicitation",
        type_="check",
    )

    # Le as solicitações e cria os schemas
    rows = bind.execute(sa.text("SELECT * FROM solicitation")).fetchall()
    solicitations: list[ClassroomSolicitationSchema] = []
    for row in rows:
        mapping = dict(row._mapping)
        mapping.pop("reservation_type", None)
        mapping.pop("status", None)

        solicitations.append(
            ClassroomSolicitationSchema(
                reservation_type=ReservationType(
                    row._mapping["reservation_type"].lower()
                ),
                status=SolicitationStatus(row._mapping["status"].lower()),
                **mapping,
            )
        )

    # Para cada solicitação, cria uma reserva (se não tiver), uma agenda e suas ocorrências

    for data in solicitations:
        classroom_id = data.classroom_id
        reservation_id = data.reservation_id

        # Se tiver reserva checa se ela existe, se não existir apaga essa solicitação (inconsistência de dados)
        # Esqueci de deixar NOT NULL em alguma migration passada
        if reservation_id:
            check = bind.execute(
                sa.text("SELECT id from reservation WHERE id = :id"),
                {"id": reservation_id},
            ).scalar()
            if not check:
                bind.execute(
                    sa.text("DELETE FROM solicitation WHERE id = :id"), {"id": data.id}
                )
                continue

        # Se não tiver reserva, cria uma, sua agenda e suas ocorrencias
        if not reservation_id:
            reservation_id = bind.execute(
                sa.text("""
                    INSERT INTO reservation
                        (title, type, reason, updated_at, created_by_id)
                    VALUES
                        (:title, :type, :reason, :updated_at, :created_by_id)
                    RETURNING id
                """),
                dict(
                    title=data.reservation_title,
                    type=str(data.reservation_type.value).upper(),
                    reason=data.reason,
                    updated_at=BrazilDatetime.now_utc(),
                    created_by_id=int(admin_id),
                ),
            ).scalar_one()

            start_date = min(data.dates) if data.dates else None
            end_date = max(data.dates) if data.dates else None
            start_time = data.start_time or time(12, 0)
            end_time = data.end_time or time(13, 0)

            schedule_id = bind.execute(
                sa.text("""
                    INSERT INTO schedule
                        (start_date, end_date, start_time, end_time,
                        classroom_id, recurrence, reservation_id, allocated, all_day)
                    VALUES
                        (:sd, :ed, :st, :et, :cid, :rec, :rid, :alloc, :all_day)
                    RETURNING id
                """),
                dict(
                    sd=start_date,
                    ed=end_date,
                    st=start_time,
                    et=end_time,
                    cid=classroom_id,
                    rec="CUSTOM",
                    rid=reservation_id,
                    alloc=False,
                    all_day=False,
                ),
            ).scalar_one()

            if data.dates:
                for d in data.dates:
                    bind.execute(
                        sa.text("""
                            INSERT INTO occurrence (date, start_time, end_time, classroom_id, schedule_id)
                            VALUES (:d, :st, :et, :cid, :sid)
                        """),
                        dict(
                            d=d,
                            st=start_time,
                            et=end_time,
                            cid=classroom_id,
                            sid=schedule_id,
                        ),
                    )

        bind.execute(
            sa.text("UPDATE solicitation SET reservation_id = :rid WHERE id = :sid"),
            {"rid": reservation_id, "sid": data.id},
        )

        bind.execute(
            sa.text("""
                INSERT INTO event (reservation_id, link, type)
                VALUES (:rid, NULL, :etype)
            """),
            {"rid": reservation_id, "etype": "OTHER"},
        )

    # Deleta as colunas antigas
    op.drop_column("solicitation", "reservation_title")
    op.drop_column("solicitation", "reservation_type")
    op.drop_column("solicitation", "start_time")
    op.drop_column("solicitation", "end_time")
    op.drop_column("solicitation", "dates")
    op.drop_column("solicitation", "reason")

    op.alter_column("solicitation", "reservation_id", nullable=False)

    # --- Exam migration ---
    op.create_table(
        "examclasslink",
        sa.Column("exam_id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["class_id"], ["class.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exam_id"], ["exam.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("exam_id", "class_id"),
    )

    op.drop_constraint("exam_class_id_fkey", "exam", type_="foreignkey")
    op.drop_column("exam", "class_id")


def downgrade() -> None:
    bind = op.get_bind()

    # --- Solicitation rollback ---
    # Rename FKS
    op.execute(
        sa.text(
            """ALTER TABLE public."solicitation" RENAME CONSTRAINT solicitation_building_id_fkey TO classroomsolicitation_building_id_fkey;"""
        )
    )
    op.execute(
        sa.text(
            """ALTER TABLE public."solicitation" RENAME CONSTRAINT solicitation_solicited_classroom_id_fkey TO classroomsolicitation_classroom_id_fkey;"""
        )
    )
    op.execute(
        sa.text(
            """ALTER TABLE public."solicitation" RENAME CONSTRAINT solicitation_user_id_fkey TO classroomsolicitation_user_id_fkey;"""
        )
    )
    op.execute(
        sa.text(
            """ALTER TABLE public."solicitation" RENAME CONSTRAINT solicitation_reservation_id_fkey TO classroomsolicitation_reservation_id_fkey;"""
        )
    )

    # Rename Constraints
    op.drop_constraint(
        "check_required_classroom_with_solicited_classroom_id_not_null",
        "solicitation",
        type_="check",
    )

    op.execute(
        sa.text(
            "ALTER TABLE solicitation RENAME COLUMN solicited_classroom_id TO classroom_id"
        )
    )

    op.create_check_constraint(
        "check_required_classroom_with_classroom_id_not_null",
        "solicitation",
        sa.text("(classroom_id IS NOT NULL) OR (required_classroom = FALSE)"),
    )

    op.add_column(
        "solicitation",
        sa.Column("reservation_title", sa.String(), nullable=True),
    )
    op.add_column(
        "solicitation",
        sa.Column(
            "reservation_type",
            sa.Enum("EXAM", "MEETING", "EVENT", "OTHER", name="reservationtype"),
            nullable=True,
        ),
    )
    op.add_column("solicitation", sa.Column("start_time", sa.Time(), nullable=True))
    op.add_column("solicitation", sa.Column("end_time", sa.Time(), nullable=True))
    op.add_column(
        "solicitation",
        sa.Column("dates", sa.ARRAY(sa.Date()), nullable=False, server_default="{}"),
    )
    op.add_column("solicitation", sa.Column("reason", sa.String(), nullable=True))

    # repopular colunas a partir de reservation/schedule/occurrence
    rows = (
        bind.execute(
            sa.text("""
        SELECT s.id AS solicitation_id,
               r.title,
               r.type,
               r.reason,
               sch.start_time,
               sch.end_time,
               COALESCE(array_agg(o.date ORDER BY o.date), '{}') AS dates
        FROM solicitation s
        LEFT JOIN reservation r ON r.id = s.reservation_id
        LEFT JOIN schedule sch ON sch.reservation_id = r.id
        LEFT JOIN occurrence o ON o.schedule_id = sch.id
        GROUP BY s.id, r.title, r.type, r.reason,
                 sch.start_time, sch.end_time
        """)
        )
        .mappings()
        .all()
    )

    for row in rows:
        bind.execute(
            sa.text("""
                UPDATE solicitation
                SET reservation_title = :title,
                    reservation_type = :rtype,
                    reason = :reason,
                    start_time = :st,
                    end_time = :et,
                    dates = :dates
                WHERE id = :sid
            """),
            dict(
                title=row["title"],
                rtype=row["type"],
                reason=row["reason"],
                st=row["start_time"],
                et=row["end_time"],
                dates=row["dates"] or [],
                sid=row["solicitation_id"],
            ),
        )

    # --- Reservation rollback ---
    # Deletar as reservas caso a solicitação não foi aprovada (e suas tabelas de especialização junto)
    # Tem que colocar um cascade delete na ordem ocorrencias -> agendas -> (eventos | reuniões | provas) -> reservas
    # Lembrando de atualizar as solicitações (tirar o reservation_id delas)
    # Além disso, voltar o classroom_id para a tabela e a constraint de FK

    # --- Reservation classroom_id column rollback ---
    # Adiciona a coluna e coloca como valor o classroom_id da sua agenda
    op.add_column("reservation", sa.Column("classroom_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "reservation_classroom_id_fkey",
        "reservation",
        "classroom",
        ["classroom_id"],
        ["id"],
    )
    bind.execute(
        sa.text("""
        UPDATE reservation
        SET classroom_id = s.classroom_id
        FROM schedule s
        WHERE s.reservation_id = reservation.id;
    """),
    )

    reservation_ids = (
        bind.execute(
            sa.text(
                "SELECT reservation_id FROM solicitation s WHERE NOT s.status = 'APPROVED'"
            )
        )
        .scalars()
        .all()
    )

    no_classroom_reservation_ids = (
        bind.execute(
            sa.text("SELECT r.id FROM reservation r WHERE r.classroom_id IS NULL")
        )
        .scalars()
        .all()
    )

    reservation_ids = list(set(reservation_ids) | set(no_classroom_reservation_ids))
    print("Reservations to delete:", len(reservation_ids))

    # Apagar as ocorrências
    bind.execute(
        sa.text("""
        DELETE FROM occurrence
        WHERE schedule_id IN (
            SELECT id FROM schedule s
            WHERE s.reservation_id = ANY(:ids)
        )
        """),
        {"ids": reservation_ids},
    )

    # Apagar as agendas
    bind.execute(
        sa.text("""
        DELETE FROM schedule s
        WHERE s.reservation_id = ANY(:ids)
        """),
        {"ids": reservation_ids},
    )

    # Apagar eventos de reservas não aprovadas/sem sala (que serão excluidas)
    bind.execute(
        sa.text("""
        DELETE FROM event e
        WHERE e.reservation_id = ANY(:ids)
        """),
        {"ids": reservation_ids},
    )

    # Apagar provas de reservas não aprovadas/sem sala (que serão excluidas)
    bind.execute(
        sa.text("""
        DELETE FROM exam e
        WHERE e.reservation_id = ANY(:ids)
        """),
        {"ids": reservation_ids},
    )

    # Apagar reuniões de reservas não aprovadas/sem sala (que serão excluidas)
    bind.execute(
        sa.text("""
        DELETE FROM meeting m
        WHERE m.reservation_id = ANY(:ids)
        """),
        {"ids": reservation_ids},
    )

    # Remove a reservation_id das solicitações não aprovadas/sem sala
    bind.execute(
        sa.text(
            "UPDATE solicitation SET reservation_id = NULL WHERE NOT status = 'APPROVED'"
        )
    )

    # Apaga todas reservas que eram de solicitações não aprovadas/ sem sala
    bind.execute(
        sa.text("""
        DELETE FROM reservation
        WHERE id = ANY(:ids)
        """),
        {"ids": reservation_ids},
    )

    # tornar colunas not null
    op.alter_column("reservation", "classroom_id", nullable=False)
    op.alter_column("solicitation", "reservation_title", nullable=False)
    op.alter_column("solicitation", "reservation_type", nullable=False)

    op.rename_table("solicitation", "classroomsolicitation")

    # --- Event rollback ---
    # Renomear evento
    op.rename_table("event", "reservationevent")
    op.execute(
        sa.text(
            """ALTER TABLE public."reservationevent" RENAME CONSTRAINT event_reservation_id_fkey TO reservationevent_reservation_id_fkey;"""
        )
    )

    # --- Exam rollback ---
    op.add_column("exam", sa.Column("class_id", sa.Integer(), nullable=True))
    op.create_foreign_key("exam_class_id_fkey", "exam", "class", ["class_id"], ["id"])

    # repopular exam.class_id a partir de examclasslink
    rows = (
        bind.execute(sa.text("SELECT exam_id, class_id FROM examclasslink"))
        .mappings()
        .all()
    )
    for row in rows:
        bind.execute(
            sa.text("UPDATE exam SET class_id = :cid WHERE id = :eid"),
            {"cid": row["class_id"], "eid": row["exam_id"]},
        )

    # dropar examclasslink
    op.drop_table("examclasslink")
