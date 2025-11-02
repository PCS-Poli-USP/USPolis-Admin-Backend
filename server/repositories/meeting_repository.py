from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import Select
from sqlmodel import Session, col, select

from server.deps.interval_dep import QueryInterval
from server.models.database.meeting_db_model import Meeting
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.models.http.requests.meeting_request_models import (
    MeetingRegister,
    MeetingUpdate,
)
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.reservation_repository import ReservationRepository


class MeetingRepository:
    @staticmethod
    def __apply_interval_filter(
        *,
        statement: Select,
        interval: QueryInterval,
    ) -> Any:
        if interval.today:
            statement = (
                statement.join(
                    Reservation, col(Meeting.reservation_id) == col(Reservation.id)
                )
                .join(Schedule, col(Schedule.reservation_id) == col(Reservation.id))
                .where(col(Schedule.end_date) >= interval.today)
            )

        if interval.start and interval.end:
            statement = (
                statement.join(
                    Reservation, col(Meeting.reservation_id) == col(Reservation.id)
                )
                .join(Schedule, col(Schedule.reservation_id) == col(Reservation.id))
                .where(
                    col(Schedule.start_date) >= interval.start,
                    col(Schedule.end_date) <= interval.end,
                )
            )
        return statement

    @staticmethod
    def get_all(*, session: Session, interval: QueryInterval) -> list[Meeting]:
        statement = select(Meeting)
        statement = MeetingRepository.__apply_interval_filter(
            statement=statement, interval=interval
        )
        return list(session.exec(statement).all())

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Meeting:
        statement = select(Meeting).where(Meeting.id == id)
        meeting = session.exec(statement).first()
        if meeting is None:
            raise MeetingNotFound()
        return meeting

    @staticmethod
    def create(
        *,
        creator: User,
        input: MeetingRegister,
        session: Session,
        allocate: bool = True,
    ) -> Meeting:
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=session
        )
        reservation = ReservationRepository.create(
            creator=creator,
            input=input,
            classroom=classroom,
            session=session,
            allocate=allocate,
        )
        meeting = Meeting(
            reservation_id=reservation.id,  # pyright: ignore[reportArgumentType]
            reservation=reservation,
            link=input.link,
        )
        session.add(meeting)
        return meeting

    @staticmethod
    def update(
        *,
        id: int,
        user: User,
        input: MeetingUpdate,
        session: Session,
    ) -> Meeting:
        meeting = MeetingRepository.get_by_id(id=id, session=session)
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=session
        )
        ReservationRepository.update(
            id=meeting.reservation_id,
            input=input,
            classroom=classroom,
            user=user,
            session=session,
        )
        meeting.link = input.link
        session.add(meeting)
        return meeting


class MeetingNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reunião não encontrada",
        )
