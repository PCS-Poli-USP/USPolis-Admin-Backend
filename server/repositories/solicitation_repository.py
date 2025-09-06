from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, select
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.database.solicitation_db_model import (
    Solicitation,
)
from server.models.database.user_db_model import User
from server.models.http.requests.solicitation_request_models import (
    SolicitationRegister,
)
from server.repositories.building_repository import BuildingRepository
from server.repositories.classroom_repository import ClassroomRepository

from server.repositories.occurrence_repository import OccurrenceRepository
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.must_be_int import must_be_int


class SolicitationRepository:
    @staticmethod
    def get_by_id(id: int, session: Session) -> Solicitation:
        statement = select(Solicitation).where(col(Solicitation.id) == id)
        try:
            solicitation = session.exec(statement).one()
        except NoResultFound:
            raise SolicitationNotFound(f"id {id}")
        return solicitation

    @staticmethod
    def get_by_user(user: User, session: Session) -> list[Solicitation]:
        statement = (
            select(Solicitation)
            .where(col(Solicitation.user_id) == user.id)
            .order_by(col(Solicitation.updated_at).desc())
        )
        solicitations = session.exec(statement).all()
        return list(solicitations)

    @staticmethod
    def get_by_buildings_ids(
        building_ids: list[int], session: Session
    ) -> list[Solicitation]:
        statement = (
            select(Solicitation)
            .where(col(Solicitation.building_id).in_(building_ids))
            .order_by(col(Solicitation.updated_at).desc())
        )
        solicitations = session.exec(statement).all()
        return list(solicitations)

    @staticmethod
    def get_by_buildings_ids_on_range(
        start: date, end: date, building_ids: list[int], session: Session
    ) -> list[Solicitation]:
        statement = (
            select(Solicitation)
            .where(
                col(Solicitation.building_id).in_(building_ids),
                col(Solicitation.created_at) >= start,
                col(Solicitation.created_at) <= end,
            )
            .order_by(col(Solicitation.updated_at).desc())
        )
        solicitations = session.exec(statement).all()
        return list(solicitations)

    @staticmethod
    def get_pending_by_buildings_ids(
        building_ids: list[int], session: Session
    ) -> list[Solicitation]:
        today = date.today()
        statement = (
            select(Solicitation)
            .join(Reservation, col(Solicitation.reservation_id) == col(Reservation.id))
            .join(Schedule, col(Reservation.id) == col(Schedule.reservation_id))
            .where(
                col(Solicitation.building_id).in_(building_ids),
                col(Reservation.status) == ReservationStatus.PENDING,
                col(Schedule.end_date) >= today,
            )
            .order_by(col(Solicitation.updated_at).desc())
        )
        solicitations = session.exec(statement).all()
        return list(solicitations)

    @staticmethod
    def create(
        requester: User, input: SolicitationRegister, session: Session
    ) -> Solicitation:
        from server.repositories.reservation_repository import ReservationRepository

        building = BuildingRepository.get_by_id(id=input.building_id, session=session)
        classroom = None
        if input.reservation_data.classroom_id:
            classroom = ClassroomRepository.get_by_id(
                id=input.reservation_data.classroom_id, session=session
            )
        if classroom and classroom.building != building:
            raise SolicitationInvalidClassroom(
                f"Solicitação: A sala {classroom.name} não pertence ao prédio {building.name}."
            )
        if classroom and not classroom.reservable:
            raise ClassroomNotReservable(f"A sala {classroom.name} não é reservável.")
        reservation = ReservationRepository.create(
            creator=requester,
            input=input.reservation_data,
            classroom=classroom,
            session=session,
            allocate=False,
        )
        solicitation = Solicitation(
            required_classroom=input.required_classroom,
            building_id=must_be_int(building.id),
            building=building,
            user_id=must_be_int(requester.id),
            user=requester,
            reservation=reservation,
            capacity=input.capacity,
        )  # pyright: ignore[reportCallIssue]
        session.add(solicitation)
        return solicitation

    @staticmethod
    def approve(
        id: int, classroom_id: int, user: User, session: Session
    ) -> Solicitation:
        solicitation = SolicitationRepository.get_by_id(id=id, session=session)
        status = solicitation.get_status()
        if status != ReservationStatus.PENDING:
            raise SolicitationAlreadyClosed(ReservationStatus.get_status_detail(status))
        SolicitationRepository.approve_solicitation_obj(
            solicitation=solicitation, user=user, session=session
        )
        classroom = solicitation.reservation.get_classroom()
        if not classroom or classroom.id != classroom_id:
            classroom = ClassroomRepository.get_by_id(id=classroom_id, session=session)

        if classroom.building_id != solicitation.building_id:
            raise SolicitationInvalidClassroom(
                f"Solicitação: A sala {classroom.name} não pertence ao prédio {solicitation.building.name}."
            )
        OccurrenceRepository.allocate_schedule(
            user=user,
            schedule=solicitation.reservation.schedule,
            classroom=classroom,
            session=session,
        )
        return solicitation

    @staticmethod
    def approve_solicitation_obj(
        solicitation: Solicitation, user: User, session: Session
    ) -> Solicitation:
        solicitation.status = ReservationStatus.APPROVED
        solicitation.closed_by = user.name
        solicitation.updated_at = BrazilDatetime.now_utc()
        session.add(solicitation)
        return solicitation

    @staticmethod
    def deny(id: int, user: User, session: Session) -> Solicitation:
        solicitation = SolicitationRepository.get_by_id(id=id, session=session)
        status = solicitation.get_status()
        if status != ReservationStatus.PENDING:
            raise SolicitationAlreadyClosed(ReservationStatus.get_status_detail(status))
        solicitation.status = ReservationStatus.DENIED
        solicitation.closed_by = user.name
        solicitation.updated_at = BrazilDatetime.now_utc()
        session.add(solicitation)
        return solicitation

    @staticmethod
    def cancel(id: int, user: User, session: Session) -> Solicitation:
        solicitation = SolicitationRepository.get_by_id(id=id, session=session)
        if not user.is_admin and solicitation.user_id != user.id:
            raise SolicitationPermissionDenied(
                "Não é permitido cancelar a solicitação de outro usuário."
            )
        solicitation.status = ReservationStatus.CANCELLED
        solicitation.closed_by = user.name
        solicitation.updated_at = BrazilDatetime.now_utc()
        session.add(solicitation)
        return solicitation


class SolicitationNotFound(HTTPException):
    def __init__(self, info: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitação {info} não encontrada",
        )


class SolicitationPermissionDenied(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class SolicitationAlreadyClosed(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class SolicitationInvalidClassroom(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ClassroomNotReservable(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
