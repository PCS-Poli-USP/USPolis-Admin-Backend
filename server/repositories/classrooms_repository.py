from sqlmodel import Session, col, select

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_request_models import ClassroomRegister


class ClassroomRepository:
    @staticmethod
    def get_all_on_building(*, building: Building, session: Session) -> list[Classroom]:
        statement = select(Classroom).where(Classroom.building_id == building.id)
        classrooms = list(session.exec(statement).all())
        return classrooms

    @staticmethod
    def get_by_id_on_building(
        classroom_id: int, *, building: Building, session: Session
    ) -> Classroom:
        classroom = session.get_one(Classroom, classroom_id)
        return classroom

    @staticmethod
    def get_by_ids(ids: list[int], *, session: Session) -> list[Classroom]:
        statement = select(Classroom).where(col(Classroom.id).in_(ids))
        classrooms = list(session.exec(statement).all())
        return classrooms

    @staticmethod
    def create(
        classroom: ClassroomRegister,
        *,
        building: Building,
        creator: User,
        session: Session,
    ) -> Classroom:
        new_classroom = Classroom(
            building=building,
            name=classroom.name,
            capacity=classroom.capacity,
            floor=classroom.floor,
            accessibility=classroom.accessibility,
            projector=classroom.projector,
            air_conditioning=classroom.air_conditioning,
            ignore_to_allocate=classroom.ignore_to_allocate,
            created_by=creator,
        )
        session.add(new_classroom)
        session.commit()
        session.refresh(new_classroom)
        return new_classroom
