from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import Select
from sqlalchemy.exc import NoResultFound
from sqlmodel import col, select, Session

from server.deps.interval_dep import QueryInterval
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.solicitation_repository import (
    SolicitationRepository,
)
from server.repositories.schedule_repository import ScheduleRepository
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.solicitation_status import SolicitationStatus
from server.utils.must_be_int import must_be_int


class ReservationRepository:
    @staticmethod
    def __apply_interval_filter(
        *,
        statement: Select,
        interval: QueryInterval,
    ) -> Any:
        if interval.today:
            statement = statement.join(Schedule).where(
                col(Schedule.end_date) >= interval.today,
            )

        if interval.start and interval.end:
            statement = statement.join(Schedule).where(
                col(Schedule.start_date) >= interval.start,
                col(Schedule.end_date) <= interval.end,
            )
        return statement

    @staticmethod
    def get_all(*, session: Session, interval: QueryInterval) -> list[Reservation]:
        statement = select(Reservation)
        statement = ReservationRepository.__apply_interval_filter(
            statement=statement, interval=interval
        )
        reservations = session.exec(statement).all()
        return list(reservations)

    @staticmethod
    def get_all_on_buildings(
        *, building_ids: list[int], session: Session, interval: QueryInterval
    ) -> list[Reservation]:
        statement = select(Reservation)
        statement = ReservationRepository.__apply_interval_filter(
            statement=statement, interval=interval
        )
        statement = (
            statement.join(
                Classroom, col(Reservation.classroom_id) == col(Classroom.id)
            )
            .join(Building, col(Classroom.building_id) == col(Building.id))
            .where(col(Building.id).in_(building_ids))
            .distinct()
        )
        reservations = list(session.exec(statement).all())
        return reservations

    @staticmethod
    def get_all_on_classrooms(
        *, classroom_ids: list[int], session: Session, interval: QueryInterval
    ) -> list[Reservation]:
        statement = select(Reservation).where(
            col(Reservation.classroom_id).in_(classroom_ids)
        )
        statement = ReservationRepository.__apply_interval_filter(
            statement=statement, interval=interval
        )
        reservations = list(session.exec(statement).all())
        return reservations

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Reservation:
        statement = select(Reservation).where(col(Reservation.id) == id)
        try:
            reservation = session.exec(statement).one()
        except NoResultFound:
            raise ReservationNotFound(id)
        return reservation

    @staticmethod
    def get_by_id_on_buildings(
        *, id: int, building_ids: list[int], session: Session
    ) -> Reservation:
        statement = (
            select(Reservation)
            .join(Classroom)
            .join(Building)
            .where(col(Building.id).in_(building_ids))
            .where(col(Reservation.id) == id)
        )
        try:
            reservation = session.exec(statement).one()
        except NoResultFound:
            raise ReservationNotFound(id)
        return reservation

    @staticmethod
    def get_by_id_on_classrooms(
        *, id: int, classroom_ids: list[int], session: Session
    ) -> Reservation:
        statement = select(Reservation).where(
            col(Reservation.id) == id, col(Reservation.classroom_id).in_(classroom_ids)
        )
        try:
            reservation = session.exec(statement).one()
        except NoResultFound:
            raise ReservationNotFound(id)
        return reservation

    @staticmethod
    def create(
        *,
        creator: User,
        input: ReservationRegister,
        classroom: Classroom,
        session: Session,
        allocate: bool = True,
    ) -> Reservation:
        reservation = Reservation(
            title=input.title,
            type=input.type,
            reason=input.reason,
            updated_at=BrazilDatetime.now_utc(),
            classroom_id=must_be_int(classroom.id),
            classroom=classroom,
            created_by_id=must_be_int(creator.id),
            created_by=creator,
        )
        schedule = ScheduleRepository.create_with_reservation(
            user=creator,
            reservation=reservation,
            input=input.schedule_data,
            classroom=classroom,
            session=session,
            allocate=allocate,
        )
        reservation.schedule = schedule
        session.add(reservation)
        return reservation

    @staticmethod
    def update_on_classrooms(
        *,
        id: int,
        classroom_ids: list[int],
        input: ReservationUpdate,
        classroom: Classroom,
        user: User,
        session: Session,
    ) -> Reservation:
        reservation = ReservationRepository.get_by_id_on_classrooms(
            id=id, classroom_ids=classroom_ids, session=session
        )
        reservation.title = input.title
        reservation.type = input.type
        reservation.reason = input.reason
        reservation.classroom = classroom

        ScheduleRepository.update_reservation_schedule(
            user=user,
            reservation=reservation,
            input=input.schedule_data,
            classroom=classroom,
            session=session,
        )
        session.add(reservation)
        return reservation

    @staticmethod
    def delete_on_buildings(
        *, id: int, building_ids: list[int], user: User, session: Session
    ) -> None:
        reservation = ReservationRepository.get_by_id_on_buildings(
            id=id, building_ids=building_ids, session=session
        )
        if reservation.solicitation:
            solicitation = SolicitationRepository.get_by_id(
                id=must_be_int(reservation.solicitation.id), session=session
            )
            solicitation.closed = True
            solicitation.closed_by = user.name
            solicitation.deleted = True
            solicitation.deleted_by = user.name
            solicitation.status = SolicitationStatus.DELETED
            OccurrenceRepository.remove_schedule_allocation(
                user=user, schedule=reservation.schedule, session=session
            )
            session.add(solicitation)
        else:
            session.delete(reservation)


class ReservationNotFound(HTTPException):
    def __init__(self, id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with id {id} not found",
        )


class ReservationWithInvalidSolicitation(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A solicitação vinculada já possui uma reserva diferente da atual",
        )
