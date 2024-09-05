from datetime import datetime
from sqlmodel import Session, col, select
from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
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
        input: ClassroomSolicitationRegister, session: Session
    ) -> ClassroomSolicitation:
        building = BuildingRepository.get_by_id(id=input.building_id, session=session)
        classroom = ClassroomRepository.get_by_id(
            id=input.classroom_id, session=session
        )
        solicitation = ClassroomSolicitation(
            classroom_id=must_be_int(classroom.id),
            classroom=classroom,
            building_id=must_be_int(building.id),
            building=building,
            date=input.date,
            reason=input.reason,
            email=input.email,
            start_time=input.start_time,
            end_time=input.end_time,
            capacity=input.capacity,
        )
        session.add(solicitation)
        return solicitation

    @staticmethod
    def approve(id: int, session: Session) -> ClassroomSolicitation:
        solicitation = ClassroomSolicitationRepository.get_by_id(id=id, session=session)
        solicitation.approved = True
        solicitation.denied = False
        solicitation.closed = True
        solicitation.updated_at = datetime.now()
        session.add(solicitation)
        return solicitation

    @staticmethod
    def deny(id: int, session: Session) -> ClassroomSolicitation:
        solicitation = ClassroomSolicitationRepository.get_by_id(id=id, session=session)
        solicitation.approved = False
        solicitation.denied = True
        solicitation.closed = True
        solicitation.updated_at = datetime.now()
        session.add(solicitation)
        return solicitation
