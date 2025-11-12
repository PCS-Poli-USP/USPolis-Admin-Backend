from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, select

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.http.requests.classroom_request_models import (
    ClassroomRegister,
    ClassroomUpdate,
)
from server.models.page_models import Page, PaginationInput
from server.utils.must_be_int import must_be_int

from server.repositories.occurrence_repository import OccurrenceRepository


class ClassroomRepository:
    @staticmethod
    def __set_classroom_core_data(
        *, classroom: Classroom, input: ClassroomRegister | ClassroomUpdate
    ) -> None:
        classroom.name = input.name
        classroom.capacity = input.capacity
        classroom.floor = input.floor
        classroom.accessibility = input.accessibility
        classroom.audiovisual = input.audiovisual
        classroom.air_conditioning = input.air_conditioning
        classroom.building_id = input.building_id
        classroom.reservable = input.reservable
        classroom.remote = input.remote
        classroom.observation = input.observation

    @staticmethod
    def get_all(*, session: Session) -> list[Classroom]:
        classrooms = list(session.exec(select(Classroom)).all())
        return classrooms

    @staticmethod
    def get_all_paginated(
        *, pagination: PaginationInput, session: Session
    ) -> Page[Classroom]:
        statement = select(Classroom)
        return Page.paginate(statement, pagination, session)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Classroom:
        statement = select(Classroom).where(Classroom.id == id)
        try:
            classroom = session.exec(statement).one()
        except NoResultFound:
            raise ClassroomNotFound(id)
        return classroom

    @staticmethod
    def get_by_ids(*, ids: list[int], session: Session) -> list[Classroom]:
        statement = select(Classroom).where(col(Classroom.id).in_(ids))
        classrooms = list(session.exec(statement).all())
        return classrooms

    @staticmethod
    def get_by_name_and_building(
        name: str, building: Building, session: Session
    ) -> Classroom:
        statement = select(Classroom).where(
            Classroom.name == name, Classroom.building_id == building.id
        )
        classroom = session.exec(statement).one()
        return classroom

    @staticmethod
    def create(
        *,
        input: ClassroomRegister,
        creator: User,
        session: Session,
    ) -> Classroom:
        new_classroom = Classroom(
            **input.model_dump(),
            created_by=creator,
            created_by_id=must_be_int(creator.id),
            groups=[],
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
        *,
        id: int,
        input: ClassroomRegister,
        building_ids: list[int],
        session: Session,
    ) -> Classroom:
        classroom = ClassroomRepository.get_by_id_on_buildings(
            id=id, building_ids=building_ids, session=session
        )
        ClassroomRepository.__set_classroom_core_data(classroom=classroom, input=input)
        session.add(classroom)
        return classroom

    @staticmethod
    def update(
        *,
        id: int,
        input: ClassroomRegister,
        session: Session,
    ) -> Classroom:
        classroom = ClassroomRepository.get_by_id(id=id, session=session)
        ClassroomRepository.__set_classroom_core_data(classroom=classroom, input=input)
        session.add(classroom)
        return classroom

    @staticmethod
    def delete_on_buildings(
        id: int, *, building_ids: list[int], user: User, session: Session
    ) -> None:
        classroom = ClassroomRepository.get_by_id_on_buildings(
            id=id, building_ids=building_ids, session=session
        )
        for schedule in classroom.schedules:
            OccurrenceRepository.remove_schedule_allocation(
                user, schedule, session=session
            )
        session.delete(classroom)

    @staticmethod
    def delete(*, id: int, user: User, session: Session) -> None:
        classroom = ClassroomRepository.get_by_id(id=id, session=session)
        for schedule in classroom.schedules:
            OccurrenceRepository.remove_schedule_allocation(
                user, schedule, session=session
            )
        session.delete(classroom)


class ClassroomNotFound(HTTPException):
    def __init__(self, id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sala com id {id} não encontrada",
        )
