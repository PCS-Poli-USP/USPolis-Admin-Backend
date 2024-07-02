from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, select

from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_request_models import ClassroomRegister


class ClassroomRepository:
    @staticmethod
    def get_all(*, session: Session) -> list[Classroom]:
        classrooms = list(session.exec(select(Classroom)).all())
        return classrooms

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Classroom:
        statement = select(Classroom).where(Classroom.id == id)
        classroom = session.exec(statement).one()
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
        creator: User,
        session: Session,
    ) -> Classroom:
        new_classroom = Classroom(
            building_id=classroom.building_id,
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
        return new_classroom

    @staticmethod
    def get_all_on_buildings(
        *, building_ids: list[int], session: Session
    ) -> list[Classroom]:
        statement = select(Classroom).where(
            col(Classroom.building_id).in_(building_ids)
        )
        classrooms = list(session.exec(statement).all())
        return classrooms

    @staticmethod
    def get_by_id_on_buildings(
        id: int, *, building_ids: list[int], session: Session
    ) -> Classroom:
        statement = (
            select(Classroom)
            .where(col(Classroom.building_id).in_(building_ids))
            .where(Classroom.id == id)
        )
        try:
            classroom = session.exec(statement).one()
        except NoResultFound:
            raise ClassroomNotFound(id)
        return classroom

    @staticmethod
    def update_on_buildings(
        id: int,
        classroom_in: ClassroomRegister,
        *,
        building_ids: list[int],
        session: Session,
    ) -> Classroom:
        classroom = ClassroomRepository.get_by_id_on_buildings(
            id=id, building_ids=building_ids, session=session
        )
        classroom.name = classroom_in.name
        classroom.capacity = classroom_in.capacity
        classroom.floor = classroom_in.floor
        classroom.ignore_to_allocate = classroom_in.ignore_to_allocate
        classroom.accessibility = classroom_in.accessibility
        classroom.projector = classroom_in.projector
        classroom.air_conditioning = classroom_in.air_conditioning
        classroom.building_id = classroom_in.building_id
        classroom.updated_at = datetime.now()
        session.add(classroom)
        return classroom

    @staticmethod
    def delete_on_buildings(
        id: int, *, building_ids: list[int], session: Session
    ) -> None:
        classroom = ClassroomRepository.get_by_id_on_buildings(
            id=id, building_ids=building_ids, session=session
        )
        session.delete(classroom)


class ClassroomNotFound(HTTPException):
    def __init__(self, id: int):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Classroom with id {id} not found")
