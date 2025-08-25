"""Update exam model and solicitation refactoring

Revision ID: 0665bcbe2878
Revises: 67f4066b6759
Create Date: 2025-08-22 19:22:47.714752

"""

from collections.abc import Sequence

from alembic import op
from pydantic import BaseModel
import sqlalchemy as sa
import sqlmodel
from sqlmodel import Field, Session, col, select
from datetime import time, date, datetime

from server.config import CONFIG

from server.models.database.user_db_model import User
from server.models.database.classroom_db_model import Classroom
from server.models.database.schedule_db_model import Schedule
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.reservation_db_model import Reservation
from server.models.database.exam_db_model import Exam
from server.models.database.event_db_model import Event

from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.event_type_enum import EventType
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.reservation_type import ReservationType
from server.utils.enums.solicitation_status import SolicitationStatus
from server.utils.must_be_int import must_be_int

# revision identifiers, used by Alembic.
revision: str = "0665bcbe2878"
down_revision: str | None = "67f4066b6759"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


class ClassroomSolicitationSchema(BaseModel):
    reservation_title: str
    reservation_type: ReservationType
    capacity: int
    start_time: time | None
    end_time: time | None
    dates: list[date] = Field(
        sa_column=sa.Column(sa.ARRAY(sa.Date), nullable=False), min_length=0
    )
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
    reservation_title: str
    reservation_type: ReservationType
    capacity: int
    start_time: time | None
    end_time: time | None
    dates: list[date] = Field(
        sa_column=sa.Column(sa.ARRAY(sa.Date), nullable=False), min_length=0
    )
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
    session = Session(bind=bind)

    op.rename_table("reservationevent", "event")

    admin = session.exec(
        select(User).where(
            col(User.is_admin) is True,
            col(User.email) == CONFIG.first_superuser_email,
        ),
    ).first()
    if not admin:
        raise Exception(f"No {CONFIG.first_superuser_email} admin user found")

    op.rename_table("classroomsolicitation", "solicitation")
    rows = bind.execute(sa.text("SELECT * FROM solicitation")).fetchall()
    solicitations: list[ClassroomSolicitationSchema] = []
    for row in rows:
        solicitations.append(ClassroomSolicitationSchema(**row._mapping))
    print(solicitations)

    filtered_solicitation = [
        s
        for s in solicitations
        if (s.status != SolicitationStatus.APPROVED and s.reservation_id is None)
    ]
    for data in filtered_solicitation:
        classroom_id = data.classroom_id
        if not classroom_id:
            stat = select(Classroom).where(
                col(Classroom.building_id) == data.building_id,
                col(Classroom.remote) is True,
            )
            classroom = session.exec(stat).first()
            if not classroom:
                raise Exception(
                    f"No remote classroom found on Building ID {data.building_id}"
                )
            classroom_id = must_be_int(classroom.id)

        reservation = Reservation(
            title=data.reservation_title,
            type=data.reservation_type,
            reason=data.reason,
            updated_at=BrazilDatetime.now_utc(),
            classroom_id=classroom_id,
            created_by_id=must_be_int(admin.id),
        )
        session.add(reservation)
        session.flush()
        solicitation.reservation_id = reservation.id

        event = Event(
            reservation=reservation,
            link=None,
            type=EventType.OTHER,
        )  # pyright: ignore[reportCallIssue]

        schedule = Schedule(
            start_date=min(solicitation.dates),
            end_date=max(solicitation.dates),
            start_time=solicitation.start_time
            if solicitation.start_time
            else time(12, 0),
            end_time=solicitation.end_time if solicitation.end_time else time(13, 0),
            classroom_id=classroom_id,
            recurrence=Recurrence.CUSTOM,
            reservation=reservation,
        )
        occurrences = []
        for d in solicitation.dates:
            occurrence = Occurrence(
                date=d,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
            )
            occurrences.append(occurrence)
            session.add(occurrence)
        schedule.occurrences = occurrences

        session.add(solicitation)
        session.add(reservation)
        session.add(event)
        session.add(schedule)

    session.commit()

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
    session = Session(bind=bind)

    exams = session.exec(select(Exam)).all()

    op.add_column(
        "exam", sa.Column("class_id", sa.INTEGER(), autoincrement=False, nullable=True)
    )
    for exam in exams:
        classes = exam.classes
        for class_ in classes:
            new_exam = Exam(
                reservation_id=exam.reservation_id,
                subject_id=exam.subject_id,
                class_id=class_.id,  # pyright: ignore[reportCallIssue]
            )
            session.add(new_exam)
        session.delete(exam)

    op.create_foreign_key("exam_class_id_fkey", "exam", "class", ["class_id"], ["id"])

    op.rename_table("event", "reservationevent")

    op.alter_column("solicitation", "reservation_id", nullable=True)
    op.add_column(
        "solicitation",
        sa.Column(
            "reservation_title",
            sqlmodel.sql.sqltypes.AutoString(),  # pyright: ignore[reportAttributeAccessIssue]
            nullable=True,  # pyright: ignore[reportAttributeAccessIssue]
        ),
    )
    op.add_column(
        "solicitation",
        sa.Column(
            "reservation_type",
            sa.Enum("EXAM", "MEETING", "EVENT", "OTHER", name="reservationtype"),
            nullable=True,
        ),
    )
    op.add_column(
        "solicitation",
        sa.Column("start_time", sa.Time(), nullable=True),
    )
    op.add_column(
        "solicitation",
        sa.Column("end_time", sa.Time(), nullable=True),
    )
    op.add_column(
        "solicitation",
        sa.Column("dates", sa.ARRAY(sa.Date()), nullable=False, server_default="{}"),
    )
    op.add_column(
        "solicitation",
        sa.Column("reason", sqlmodel.sql.sqltypes.AutoString(), nullable=True),  # pyright: ignore[reportAttributeAccessIssue]
    )
    op.add_column(
        "solicitation", sa.Column("classroom_id", sa.Integer(), nullable=True)
    )
    op.create_check_constraint(
        constraint_name="check_required_classroom_with_classroom_id_not_null",
        table_name="solicitation",
        condition=sa.text("classroom_id IS NOT NULL"),
    )
    op.create_foreign_key(
        "classroomsolicitation_classroom_id_fkey",
        "solicitation",
        "classroom",
        ["classroom_id"],
        ["id"],
    )
    rows = bind.execute(sa.text("SELECT * FROM solicitation")).fetchall()
    solicitations: list[SolicitationDowngradeSchema] = []
    for row in rows:
        solicitations.append(SolicitationDowngradeSchema(**row._mapping))

    for solicitation in solicitations:
        reservation = session.exec(
            select(Reservation).where(Reservation.id == solicitation.reservation_id)
        ).one()

        solicitation.reservation_title = reservation.title
        solicitation.reservation_type = reservation.type
        solicitation.reason = reservation.reason
        solicitation.start_time = reservation.schedule.start_time
        solicitation.end_time = reservation.schedule.end_time
        dates = [occurrence.date for occurrence in reservation.schedule.occurrences]
        solicitation.dates = dates

        if solicitation.status != SolicitationStatus.APPROVED:
            session.delete(reservation)

        session.add(solicitation)

    session.commit()
    op.alter_column("solicitation", "reservation_title", nullable=False)
    op.alter_column("solicitation", "reservation_type", nullable=False)
    op.rename_table("solicitation", "classroomsolicitation")

    op.drop_table("examclasslink")
