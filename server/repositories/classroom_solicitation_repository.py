from datetime import datetime
from sqlmodel import Session, col, select
from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_solicitation_request_models import (
    ClassroomSolicitationRegister,
)
from server.repositories.building_repository import BuildingRepository
from server.repositories.classroom_repository import ClassroomRepository
from server.utils.must_be_int import must_be_int


class ClassroomSolicitationRepository:
    @staticmethod
    def get_by_id(id: int, session: Session) -> ClassroomSolicitation:
        statement = select(ClassroomSolicitation).where(
            col(ClassroomSolicitation.id) == id
        )
        solicitation = session.exec(statement).one()
        return solicitation

    @staticmethod
    def get_by_id_on_buildings(
        building_ids: list[int], session: Session
    ) -> list[ClassroomSolicitation]:
        statement = select(ClassroomSolicitation).where(
            col(ClassroomSolicitation.building_id).in_(building_ids)
        )
        solicitations = session.exec(statement).all()
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
        )
        session.add(solicitation)
        return solicitation

    @staticmethod
    def approve(id: int, user: User, session: Session) -> ClassroomSolicitation:
        solicitation = ClassroomSolicitationRepository.get_by_id(id=id, session=session)
        solicitation.approved = True
        solicitation.denied = False
        solicitation.closed = True
        solicitation.closed_by = user.name
        solicitation.updated_at = datetime.now()
        session.add(solicitation)
        return solicitation

    @staticmethod
    def deny(id: int, user: User, session: Session) -> ClassroomSolicitation:
        solicitation = ClassroomSolicitationRepository.get_by_id(id=id, session=session)
        solicitation.approved = False
        solicitation.denied = True
        solicitation.closed = True
        solicitation.closed_by = user.name
        solicitation.updated_at = datetime.now()
        session.add(solicitation)
        return solicitation
