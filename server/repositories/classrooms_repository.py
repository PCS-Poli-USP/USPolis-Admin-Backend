from datetime import datetime

from sqlmodel import Session, select

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_request_models import ClassroomRegister


class ClassroomRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Classroom]:
        classrooms = list(session.exec(select(Classroom)).all())
        return classrooms

    @staticmethod
    def get_by_id(id: int, *, session: Session) -> Classroom:
        classroom = session.exec(select(Classroom).where(Classroom.id == id)).one()
        return classroom

    @staticmethod
    def create(
        classroom: ClassroomRegister,
        *,
        building: Building,
        creator: User | None,
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

    @staticmethod
    def get_all_on_building(*, building: Building, session: Session) -> list[Classroom]:
        statement = select(Classroom).where(Classroom.building_id == building.id)
        classrooms = list(session.exec(statement).all())
        return classrooms

    @staticmethod
    def get_by_id_on_building(
        id: int, *, building: Building, session: Session
    ) -> Classroom:
        statement = (
            select(Classroom)
            .where(Classroom.building_id == building.id)
            .where(Classroom.id == id)
        )
        classroom = session.exec(statement).one()
        return classroom

    @staticmethod
    def update_on_building(
        id: int,
        classroom_in: ClassroomRegister,
        *,
        building: Building,
        session: Session,
    ) -> Classroom:
        classroom = ClassroomRepository.get_by_id_on_building(
            id=id, building=building, session=session
        )
        classroom.name = classroom_in.name
        classroom.capacity = classroom_in.capacity
        classroom.floor = classroom_in.floor
        classroom.ignore_to_allocate = classroom_in.ignore_to_allocate
        classroom.accessibility = classroom_in.accessibility
        classroom.projector = classroom_in.projector
        classroom.air_conditioning = classroom_in.air_conditioning
        classroom.updated_at = datetime.now()
        session.add(classroom)
        session.commit()
        session.refresh(classroom)
        return classroom

    @staticmethod
    def delete_on_building(id: int, *, building: Building, session: Session) -> None:
        classroom = ClassroomRepository.get_by_id_on_building(
            id=id, building=building, session=session
        )
        session.delete(classroom)
        session.commit()
