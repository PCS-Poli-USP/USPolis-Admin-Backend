from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, select
from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_solicitation_request_models import (
    ClassroomSolicitationRegister,
)
from server.repositories.building_repository import BuildingRepository
from server.repositories.classroom_repository import ClassroomRepository
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.solicitation_status import SolicitationStatus
from server.utils.must_be_int import must_be_int


class ClassroomSolicitationRepository:
    @staticmethod
    def get_by_id(id: int, session: Session) -> ClassroomSolicitation:
        statement = select(ClassroomSolicitation).where(
            col(ClassroomSolicitation.id) == id
        )
        try:
            solicitation = session.exec(statement).one()
        except NoResultFound:
            raise ClassroomSolicitationNotFound(f"id {id}")
        return solicitation

    @staticmethod
    def get_by_user(user: User, session: Session) -> list[ClassroomSolicitation]:
        statement = (
            select(ClassroomSolicitation)
            .where(col(ClassroomSolicitation.user_id) == user.id)
            .order_by(col(ClassroomSolicitation.updated_at).desc())
        )
        solicitations = session.exec(statement).all()
        return list(solicitations)

    @staticmethod
    def get_by_buildings_ids(
        building_ids: list[int], session: Session
    ) -> list[ClassroomSolicitation]:
        statement = (
            select(ClassroomSolicitation)
            .where(col(ClassroomSolicitation.building_id).in_(building_ids))
            .order_by(col(ClassroomSolicitation.updated_at).desc())
        )
        solicitations = session.exec(statement).all()
        return list(solicitations)

    @staticmethod
    def get_by_buildings_ids_on_range(
        start: date, end: date, building_ids: list[int], session: Session
    ) -> list[ClassroomSolicitation]:
        statement = (
            select(ClassroomSolicitation)
            .where(
                col(ClassroomSolicitation.building_id).in_(building_ids),
                col(ClassroomSolicitation.created_at) >= start,
                col(ClassroomSolicitation.created_at) <= end,
            )
            .order_by(col(ClassroomSolicitation.updated_at).desc())
        )
        solicitations = session.exec(statement).all()
        return list(solicitations)

    @staticmethod
    def get_pending_by_buildings_ids(
        building_ids: list[int], session: Session
    ) -> list[ClassroomSolicitation]:
        today = date.today()
        statement = (
            select(ClassroomSolicitation)
            .where(
                col(ClassroomSolicitation.building_id).in_(building_ids),
                col(ClassroomSolicitation.status) == SolicitationStatus.PENDING,
            )
            .order_by(col(ClassroomSolicitation.updated_at).desc())
        )
        solicitations = session.exec(statement).all()
        solicitations = [
            solicitation
            for solicitation in solicitations
            if max(solicitation.dates) >= today
        ]
        return list(solicitations)

    @staticmethod
    def create(
        requester: User, input: ClassroomSolicitationRegister, session: Session
    ) -> ClassroomSolicitation:
        building = BuildingRepository.get_by_id(id=input.building_id, session=session)
        classroom = None
        if input.classroom_id:
            classroom = ClassroomRepository.get_by_id(
                id=input.classroom_id, session=session
            )
        solicitation = ClassroomSolicitation(
            classroom_id=must_be_int(classroom.id) if classroom else None,
            classroom=classroom,
            required_classroom=input.required_classroom,
            building_id=must_be_int(building.id),
            building=building,
            user_id=must_be_int(requester.id),
            user=requester,
            dates=input.dates,
            reason=input.reason,
            reservation_id=None,
            reservation_title=input.reservation_title,
            reservation_type=input.reservation_type,
            start_time=input.start_time,
            end_time=input.end_time,
            capacity=input.capacity,
            status=SolicitationStatus.PENDING,
        )
        session.add(solicitation)
        return solicitation

    @staticmethod
    def approve(id: int, user: User, session: Session) -> ClassroomSolicitation:
        solicitation = ClassroomSolicitationRepository.get_by_id(id=id, session=session)
        ClassroomSolicitationRepository.approve_solicitation_obj(
            solicitation=solicitation, user=user, session=session
        )
        return solicitation

    @staticmethod
    def approve_solicitation_obj(
        solicitation: ClassroomSolicitation, user: User, session: Session
    ) -> ClassroomSolicitation:
        solicitation.status = SolicitationStatus.APPROVED
        solicitation.closed_by = user.name
        solicitation.updated_at = BrazilDatetime.now_utc()
        session.add(solicitation)
        return solicitation

    @staticmethod
    def deny(id: int, user: User, session: Session) -> ClassroomSolicitation:
        solicitation = ClassroomSolicitationRepository.get_by_id(id=id, session=session)
        solicitation.status = SolicitationStatus.DENIED
        solicitation.closed_by = user.name
        solicitation.updated_at = BrazilDatetime.now_utc()
        session.add(solicitation)
        return solicitation
    
    @staticmethod
    def cancel(id: int, user: User, session: Session) -> ClassroomSolicitation:
        solicitation = ClassroomSolicitationRepository.get_by_id(id=id, session=session)
        if not user.is_admin and solicitation.user_id != user.id:
            raise ClassroomSolicitationPermissionDenied("Não é permitido cancelar a solicitação de outro usuário.")
        solicitation.status = SolicitationStatus.CANCELLED
        solicitation.closed_by = user.name
        solicitation.updated_at = BrazilDatetime.now_utc()
        session.add(solicitation)
        return solicitation


class ClassroomSolicitationNotFound(HTTPException):
    def __init__(self, info: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Solicitação {info} não encontrada",
        )

class ClassroomSolicitationPermissionDenied(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )