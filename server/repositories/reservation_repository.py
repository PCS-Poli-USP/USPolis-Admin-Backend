from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import col, select, Session

from server.models.database.reservation_db_model import Reservation
from server.models.database.user_db_model import User
from server.models.http.requests.reservation_request_models import ReservationRegister
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.schedule_repository import ScheduleRepository


class ReservationRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Reservation]:
        statement = select(Reservation)
        reservations = session.exec(statement).all()
        return list(reservations)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Reservation:
        statement = select(Reservation).where(col(Reservation.id) == id)
        reservation = session.exec(statement).one()
        return reservation

    @staticmethod
    def create(*, creator: User, input: ReservationRegister, session: Session) -> Reservation:
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=session)
        reservation = Reservation(
            name=input.name,
            type=input.type,
            description=input.description,
            updated_at=datetime.now(),
            classroom=classroom,
            created_by=creator,
        )
        schedule = ScheduleRepository.create_with_reservation(
            reservation=reservation, input=input.schedule_data, session=session)
        reservation.schedule = schedule
        session.add(reservation)
        return reservation
