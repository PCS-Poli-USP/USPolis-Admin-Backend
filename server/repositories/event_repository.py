from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import Select
from sqlmodel import Session, col, select
from server.deps.interval_dep import QueryInterval
from server.models.database.event_db_model import Event
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.models.http.requests.event_request_models import EventRegister, EventUpdate
from server.models.http.requests.solicitation_request_models import EventSolicitation
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.reservation_repository import ReservationRepository


class EventRepository:
    @staticmethod
    def __apply_interval_filter(
        *,
        statement: Select,
        interval: QueryInterval,
    ) -> Any:
        if interval.today:
            statement = (
                statement.join(
                    Reservation, col(Event.reservation_id) == col(Reservation.id)
                )
                .join(Schedule, col(Schedule.reservation_id) == col(Reservation.id))
                .where(col(Schedule.end_date) >= interval.today)
            )

        if interval.start and interval.end:
            statement = (
                statement.join(
                    Reservation, col(Event.reservation_id) == col(Reservation.id)
                )
                .join(Schedule, col(Schedule.reservation_id) == col(Reservation.id))
                .where(
                    col(Schedule.start_date) >= interval.start,
                    col(Schedule.end_date) <= interval.end,
                )
            )
        return statement

    @staticmethod
    def get_all(*, session: Session, interval: QueryInterval) -> list[Event]:
        statement = select(Event)
        statement = EventRepository.__apply_interval_filter(
            statement=statement, interval=interval
        )
        return list(session.exec(statement).all())

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Event:
        statement = select(Event).where(Event.id == id)
        event = session.exec(statement).first()
        if event is None:
            raise EventNotFound()
        return event

    @staticmethod
    def create(
        *,
        creator: User,
        input: EventRegister | EventSolicitation,
        session: Session,
        allocate: bool = True,
    ) -> Event:
        classroom = None
        if input.classroom_id:
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
        event = Event(
            reservation=reservation,
            link=input.link,
            type=input.event_type,
        )  # pyright: ignore[reportCallIssue]
        session.add(event)
        return event

    @staticmethod
    def update(*, user: User, id: int, input: EventUpdate, session: Session) -> Event:
        event = EventRepository.get_by_id(id=id, session=session)
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=session
        )
        ReservationRepository.update(
            id=event.reservation_id,
            input=input,
            classroom=classroom,
            user=user,
            session=session,
        )  # pyright: ignore[reportArgumentType]
        event.link = input.link
        event.type = input.event_type
        session.add(event)
        return event


class EventNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado",
        )
