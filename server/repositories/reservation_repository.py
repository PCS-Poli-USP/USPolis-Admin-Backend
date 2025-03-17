from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import col, select, Session

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.database.reservation_db_model import Reservation
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_solicitation_request_models import (
    ClassroomSolicitationApprove,
)
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)
from server.models.http.requests.schedule_request_models import ScheduleRegister
from server.repositories.schedule_repository import ScheduleRepository
from server.utils.enums.recurrence import Recurrence
from server.utils.must_be_int import must_be_int


class ReservationRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Reservation]:
        statement = select(Reservation)
        reservations = session.exec(statement).all()
        return list(reservations)

    @staticmethod
    def get_all_on_buildings(
        *, building_ids: list[int], session: Session
    ) -> list[Reservation]:
        statement = (
            select(Reservation)
            .join(Classroom)
            .join(Building)
            .where(col(Building.id).in_(building_ids))
            .distinct()
        )
        reservations = list(session.exec(statement).all())
        return reservations

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Reservation:
        statement = select(Reservation).where(col(Reservation.id) == id)
        reservation = session.exec(statement).one()
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
            updated_at=datetime.now(),
            classroom_id=must_be_int(classroom.id),
            classroom=classroom,
            created_by_id=must_be_int(creator.id),
            created_by=creator,
        )
        schedule = ScheduleRepository.create_with_reservation(
            reservation=reservation,
            input=input.schedule_data,
            classroom=classroom,
            session=session,
        )
        reservation.schedule = schedule
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
            updated_at=datetime.now(),
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
            reservation=reservation,
            input=schedule_input,
            classroom=classroom,
            session=session,
        )
        session.add(schedule)
        reservation.schedule = schedule
        return reservation

    @staticmethod
    def update_on_buildings(
        *,
        id: int,
        building_ids: list[int],
        input: ReservationUpdate,
        classroom: Classroom,
        session: Session,
    ) -> Reservation:
        reservation = ReservationRepository.get_by_id_on_buildings(
            id=id, building_ids=building_ids, session=session
        )
        reservation.title = input.title
        reservation.type = input.type
        reservation.reason = input.reason
        reservation.classroom = classroom

        ScheduleRepository.update_reservation_schedule(
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
        if (reservation.solicitation):
            reservation.solicitation.reservation = None
            reservation.solicitation.deleted = True
            reservation.solicitation.deleted_by = user.name
            session.add(reservation.solicitation)
        session.delete(reservation)


class ReservationNotFound(HTTPException):
    def __init__(self, id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with id {id} not found",
        )
