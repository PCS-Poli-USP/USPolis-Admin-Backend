from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import Select
from sqlalchemy.exc import NoResultFound
from sqlmodel import col, select, Session

from server.deps.interval_dep import QueryInterval
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_solicitation_request_models import (
    ClassroomSolicitationApprove,
)
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)
from server.models.http.requests.schedule_request_models import ScheduleRegister
from server.repositories.classroom_solicitation_repository import (
    ClassroomSolicitationRepository,
)
from server.repositories.schedule_repository import ScheduleRepository
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.recurrence import Recurrence
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
        )
        reservation.schedule = schedule
        if input.has_solicitation and input.solicitation_id:
            solicitation = ClassroomSolicitationRepository.get_by_id(
                id=input.solicitation_id, session=session
            )
            if solicitation.reservation_id:
                raise ReservationWithInvalidSolicitation()
            reservation.solicitation = solicitation
            solicitation.reservation_id = reservation.id
            solicitation.reservation = reservation
            solicitation.classroom_id = classroom.id
            solicitation.classroom = classroom
            ClassroomSolicitationRepository.approve_solicitation_obj(
                solicitation, user=creator, session=session
            )
            session.add(solicitation)
        session.add(reservation)
        return reservation

    @staticmethod
    def create_by_solicitation(
        creator: User,
        input: ClassroomSolicitationApprove,
        solicitation: ClassroomSolicitation,
        classroom: Classroom,
        session: Session,
    ) -> Reservation:
        reservation = Reservation(
            title=solicitation.reservation_title,
            type=solicitation.reservation_type,
            reason=solicitation.reason,
            updated_at=BrazilDatetime.now_utc(),
            classroom_id=must_be_int(classroom.id),
            classroom=classroom,
            created_by_id=must_be_int(creator.id),
            created_by=creator,
            solicitation=solicitation,
        )
        session.add(reservation)
        schedule_input = ScheduleRegister(
            dates=solicitation.dates,
            start_date=min(solicitation.dates),
            end_date=max(solicitation.dates),
            recurrence=Recurrence.CUSTOM,
            start_time=input.start_time,
            end_time=input.end_time,
            allocated=True,
            reservation_id=reservation.id,
            classroom_id=classroom.id,
        )
        schedule = ScheduleRepository.create_with_reservation(
            user=creator,
            reservation=reservation,
            input=schedule_input,
            classroom=classroom,
            session=session,
        )
        session.add(schedule)
        reservation.schedule = schedule
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
        if input.has_solicitation and input.solicitation_id:
            if (
                reservation.solicitation
                and reservation.solicitation.id != input.solicitation_id
            ):
                raise ReservationWithInvalidSolicitation()
            solicitation = ClassroomSolicitationRepository.get_by_id(
                id=input.solicitation_id, session=session
            )
            if (
                solicitation.reservation_id
                and solicitation.reservation_id != reservation.id
            ):
                raise ReservationWithInvalidSolicitation()
            if not reservation.solicitation:
                reservation.solicitation = solicitation
                solicitation.reservation = reservation
                session.add(solicitation)

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
            solicitation = ClassroomSolicitationRepository.get_by_id(
                id=must_be_int(reservation.solicitation.id), session=session
            )
            solicitation.deleted = True
            solicitation.deleted_by = user.name
            solicitation.reservation = None
            solicitation.reservation_id = None
            reservation.solicitation = None
            session.add(solicitation)
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
