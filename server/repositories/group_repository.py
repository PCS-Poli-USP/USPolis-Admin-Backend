from datetime import datetime
from sqlmodel import Session, col, select
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException, status

from server.models.database.group_db_model import Group
from server.models.http.requests.group_request_models import GroupRegister, GroupUpdate
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.user_repository import UserRepository


class GroupRepository:
    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Group:
        statement = select(Group).where(col(Group.id) == id)
        try:
            group = session.exec(statement).one()
        except NoResultFound:
            raise GroupNotFound(f"id {id}")
        return group

    @staticmethod
    def get_all(*, session: Session) -> list[Group]:
        statment = select(Group)
        groups = session.exec(statment).all()
        return list(groups)

    @staticmethod
    def create(*, input: GroupRegister, session: Session) -> Group:
        group = Group(
            name=input.name,
            abbreviation=input.abbreviation,
        )
        if input.classroom_ids:
            group.classrooms = ClassroomRepository.get_by_ids(
                ids=input.classroom_ids, session=session
            )
        if input.user_ids:
            group.users = UserRepository.get_by_ids(ids=input.user_ids, session=session)
        session.add(group)
        return group

    @staticmethod
    def update(*, id: int, input: GroupUpdate, session: Session) -> Group:
        group = GroupRepository.get_by_id(id=id, session=session)
        group.name = input.name
        group.abbreviation = input.abbreviation
        group.updated_at = datetime.now()
        if set(input.classroom_ids) != set(
            [classroom.id for classroom in group.classrooms]
        ):
            group.classrooms = ClassroomRepository.get_by_ids(
                ids=input.classroom_ids, session=session
            )
        if set(input.user_ids) != set([user.id for user in group.users]):
            group.users = UserRepository.get_by_ids(ids=input.user_ids, session=session)
        session.add(group)
        return group

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        group = GroupRepository.get_by_id(id=id, session=session)
        session.delete(group)


class GroupNotFound(HTTPException):
    def __init__(self, info: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grupo com {info} não encontrado",
        )
