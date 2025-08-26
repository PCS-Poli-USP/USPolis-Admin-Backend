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


class SolicitationDowngradeSchema(BaseModel):
    id: int
    reservation_title: str
    reservation_type: ReservationType
    capacity: int
    start_time: time | None
    end_time: time | None
    dates: list[date]
    reason: str | None
    status: SolicitationStatus
    closed_by: str | None
    deleted_by: str | None
    created_at: datetime
    updated_at: datetime
    user_id: int
    building_id: int
    classroom_id: int | None
    reservation_id: int


def upgrade() -> None:
    bind = op.get_bind()

    op.rename_table("reservationevent", "event")

    admin_id = bind.execute(
        sa.text("""
            SELECT id FROM "user" WHERE email = :email LIMIT 1
        """),
        {"email": CONFIG.first_superuser_email},
    ).scalar()
    if not admin_id:
        raise Exception(f"No {CONFIG.first_superuser_email} admin user found")

    op.rename_table("classroomsolicitation", "solicitation")
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

    for data in solicitations:
        # Caso a solicitação já foi aprovada e tem uma reserva
        if data.status == SolicitationStatus.APPROVED:
            if not data.reservation_id:
                raise Exception(
                    f"Solicitation ID {data.id} is approved but has no reservation_id"
                )

            r_id = bind.execute(
                sa.text("""
                    SELECT classroom_id
                    FROM reservation
                    WHERE id = :rid
                    LIMIT 1
                """),
                {"rid": data.reservation_id},
            ).scalar()
            if not r_id:
                raise Exception(
                    f"Solicitation ID {data.id} has reservation_id {data.reservation_id} but no classroom_id found on reservation"
                )
            bind.execute(
                sa.text("""
                INSERT INTO event (reservation_id, link, type)
                VALUES (:rid, NULL, :etype)
            """),
                {"rid": r_id, "etype": "OTHER"},
            )
            continue

        classroom_id = data.classroom_id
        if not classroom_id:
            classroom_id = bind.execute(
                sa.text("""
                    SELECT id
                    FROM classroom
                    WHERE building_id = :bid AND remote = true
                    LIMIT 1
                """),
                {"bid": data.building_id},
            ).scalar()

            if not classroom_id:
                raise Exception(
                    f"No remote classroom found on Building ID {data.building_id}"
                )

        reservation_id = bind.execute(
            sa.text("""
                INSERT INTO reservation
                    (title, type, reason, updated_at, classroom_id, created_by_id)
                VALUES
                    (:title, :type, :reason, :updated_at, :classroom_id, :created_by_id)
                RETURNING id
            """),
            dict(
                title=data.reservation_title,
                type=str(data.reservation_type.value).upper(),
                reason=data.reason,
                updated_at=BrazilDatetime.now_utc(),
                classroom_id=classroom_id,
                created_by_id=int(admin_id),
            ),
        ).scalar_one()

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
                        INSERT INTO occurrence (date, start_time, end_time, schedule_id)
                        VALUES (:d, :st, :et, :sid)
                    """),
                    dict(
                        d=d,
                        st=start_time,
                        et=end_time,
                        sid=schedule_id,
                    ),
                )

    op.drop_column("solicitation", "reservation_title")
    op.drop_column("solicitation", "reservation_type")
    op.drop_column("solicitation", "start_time")
    op.drop_column("solicitation", "end_time")
    op.drop_column("solicitation", "dates")
    op.drop_column("solicitation", "reason")
    op.drop_constraint(
        "check_required_classroom_with_classroom_id_not_null",
        "solicitation",
        type_="check",
    )
    op.drop_column("solicitation", "classroom_id")
    op.alter_column("solicitation", "reservation_id", nullable=False)

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
    op.alter_column("solicitation", "reservation_id", nullable=True)
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
    op.add_column(
        "solicitation", sa.Column("classroom_id", sa.Integer(), nullable=True)
    )

    op.create_foreign_key(
        "classroomsolicitation_classroom_id_fkey",
        "solicitation",
        "classroom",
        ["classroom_id"],
        ["id"],
    )

    # repopular colunas a partir de reservation/schedule/occurrence
    rows = (
        bind.execute(
            sa.text("""
        SELECT s.id as solicitation_id, r.title, r.type, r.reason, r.classroom_id,
               sch.start_time, sch.end_time, array_agg(o.date ORDER BY o.date) as dates
        FROM solicitation s
        JOIN reservation r ON r.id = s.reservation_id
        LEFT JOIN schedule sch ON sch.reservation_id = r.id
        LEFT JOIN occurrence o ON o.schedule_id = sch.id
        GROUP BY s.id, r.title, r.type, r.reason, r.classroom_id, sch.start_time, sch.end_time
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
                    classroom_id = :cid,
                    start_time = :st,
                    end_time = :et,
                    dates = :dates
                WHERE id = :sid
            """),
            dict(
                title=row["title"],
                rtype=row["type"],
                reason=row["reason"],
                cid=row["classroom_id"],
                st=row["start_time"],
                et=row["end_time"],
                dates=row["dates"] or [],
                sid=row["solicitation_id"],
            ),
        )

    op.create_check_constraint(
        "check_required_classroom_with_classroom_id_not_null",
        "solicitation",
        sa.text("(classroom_id IS NOT NULL) OR (required_classroom = FALSE)"),
    )

    # Deletar as reservas caso a solicitação não foi aprovada (e suas tabelas de especialização junto)
    # Tem que colocar um cascade delete na ordem ocorrencias -> agendas -> (eventos | reuniões | provas) -> reservas
    # Lembrando de atualizar as solicitações (tirar o reservation_id delas)

    # Apagar as ocorrências
    bind.execute(
        sa.text("""
        DELETE FROM occurrence
        WHERE schedule_id IN (
            SELECT id FROM schedule
            WHERE reservation_id IN (
                SELECT reservation_id FROM solicitation WHERE NOT status = 'APPROVED'
            )
        )
        """)
    )

    # Apagar as agendas
    bind.execute(
        sa.text("""
        DELETE FROM schedule
        WHERE reservation_id IN (
            SELECT reservation_id FROM solicitation WHERE NOT status = 'APPROVED'
        )
        """)
    )

    # Apagar eventos de reservas não aprovadas (que serão excluidas)
    bind.execute(
        sa.text("""
        DELETE FROM event
        WHERE reservation_id IN (
            SELECT reservation_id FROM solicitation WHERE NOT status = 'APPROVED'
        )
        """)
    )

    # Apagar provas de reservas não aprovadas (que serão excluidas)
    bind.execute(
        sa.text("""
        DELETE FROM exam
        WHERE reservation_id IN (
            SELECT reservation_id FROM solicitation WHERE NOT status = 'APPROVED'
        )
        """)
    )

    # Apagar reuniões de reservas não aprovadas (que serão excluidas)
    bind.execute(
        sa.text("""
        DELETE FROM meeting
        WHERE reservation_id IN (
            SELECT reservation_id FROM solicitation WHERE NOT status = 'APPROVED'
        )
        """)
    )

    # Pega todos ids de reservas a partir das solicitações não aprovadas
    reservation_ids = (
        bind.execute(
            sa.text(
                "SELECT reservation_id FROM solicitation WHERE NOT status = 'APPROVED'"
            )
        )
        .scalars()
        .all()
    )

    # Remove a reservation_id das solicitações não aprovadas
    bind.execute(
        sa.text(
            "UPDATE solicitation SET reservation_id = NULL WHERE NOT status = 'APPROVED'"
        )
    )

    # Apaga todas reservas que eram de solicitações não aprovadas
    bind.execute(
        sa.text("""
        DELETE FROM reservation
        WHERE id = ANY(:ids)
        """),
        {"ids": reservation_ids},
    )

    # tornar colunas not null
    op.alter_column("solicitation", "reservation_title", nullable=False)
    op.alter_column("solicitation", "reservation_type", nullable=False)

    # renomear de volta
    op.rename_table("event", "reservationevent")
    op.rename_table("solicitation", "classroomsolicitation")

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
