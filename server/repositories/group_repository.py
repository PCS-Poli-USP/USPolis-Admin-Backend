from datetime import datetime
from sqlmodel import Session, col, select
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException, status

from server.models.database.building_db_model import Building
from server.models.database.group_classroom_link import GroupClassroomLink
from server.models.database.group_db_model import Group
from server.models.database.group_user_link import GroupUserLink
from server.models.database.user_db_model import User
from server.models.http.requests.group_request_models import GroupRegister, GroupUpdate
from server.repositories.building_repository import BuildingRepository
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.user_repository import UserRepository


class GroupRepository:
    @staticmethod
    def __remove_users_from_group(
        *,
        group: Group,
        users: list[User],
        session: Session,
    ) -> None:
        """Remove users from a group, keeping correctly the users buildings defined by his groups.\n
        The function will assume that the users are already in the group.\n
        """
        for user in users:
            user.groups.remove(group)
            remaining_groups_on_building = [
                g for g in user.groups if g.building_id == group.building_id
            ]
            if len(remaining_groups_on_building) == 0:
                if user.buildings is not None:
                    user.buildings.remove(group.building)
            session.add(user)

    @staticmethod
    def __update_group_users(
        *,
        group: Group,
        user_ids: list[int],
        session: Session,
    ) -> None:
        """Update group users, keeping correctly the users buildings defined by his groups.\n"""
        users = UserRepository.get_by_ids(ids=user_ids, session=session)
        for user in users:
            user_building_ids = user.buildings_ids_set()
            if group.building_id not in user_building_ids:
                if user.buildings is None:
                    user.buildings = [group.building]
                else:
                    user.buildings.append(group.building)
            session.add(user)
        group.users = users

    @staticmethod
    def __check_group_validation(
        *,
        group: Group,
        building_id: int,
        classroom_ids: list[int] | None,
        session: Session,
    ) -> None:
        """Check group classrooms validation.\n
        A group is valid when:
        - The group has at least one classroom
        - Only the main group not have classrooms
        - The group classrooms are all in the same building
        - A not main group can not have all classrooms of the building

        This method will update the group classrooms and main group status.\n

        """
        if not classroom_ids and not group.main:
            raise GroupWithoutClassroom(group.name)

        if group.main and classroom_ids:
            raise MainGroupWithClassrooms()

        main = GroupRepository.get_building_main_group(
            building_id=building_id, session=session
        )
        if main and group.main and main.id != group.id:
            raise MainGroupIsUnique()

        building = BuildingRepository.get_by_id(id=building_id, session=session)
        classrooms = ClassroomRepository.get_by_ids(
            ids=classroom_ids if classroom_ids else [], session=session
        )
        for classroom in classrooms:
            if classroom.building_id != building_id:
                raise GroupWithMultipleBuildings(group.name)
        group.classrooms = classrooms

        group_has_all_classrooms = False
        if not group.main:
            building_set = building.get_classrooms_ids_set()
            classrooms_set = set([classroom.id for classroom in classrooms])
            group_has_all_classrooms = (
                True
                if building_set == classrooms_set and len(building_set) != 0
                else False
            )

        if group_has_all_classrooms:
            raise GroupWithAllClassrooms(building.name)

        session.add(group)

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> Group:
        statement = select(Group).where(col(Group.id) == id)
        try:
            group = session.exec(statement).one()
        except NoResultFound:
            raise GroupNotFound(f"id {id}")
        return group

    @staticmethod
    def get_by_ids(*, ids: list[int], session: Session) -> list[Group]:
        statement = select(Group).where(col(Group.id).in_(ids))
        groups = session.exec(statement).all()
        return list(groups)

    @staticmethod
    def get_building_main_group(*, building_id: int, session: Session) -> Group | None:
        statement = select(Group).where(
            col(Group.building_id) == building_id, col(Group.main)
        )
        group = session.exec(statement).first()
        return group

    @staticmethod
    def get_by_user_id(*, user_id: int, session: Session) -> list[Group]:
        statement = (
            select(Group)
            .join(GroupUserLink)
            .where(
                col(GroupUserLink.group_id) == col(Group.id),
                col(GroupUserLink.user_id) == user_id,
            )
        )
        groups = session.exec(statement).all()
        return list(groups)

    @staticmethod
    def get_by_classroom_id(*, classroom_id: int, session: Session) -> list[Group]:
        statement = (
            select(Group)
            .join(GroupClassroomLink)
            .where(
                col(GroupClassroomLink.classroom_id) == classroom_id,
                col(GroupClassroomLink.group_id) == col(Group.id),
            )
        )
        groups = session.exec(statement).all()
        return list(groups)

    @staticmethod
    def get_all(*, session: Session) -> list[Group]:
        statement = (
            select(Group)
            .join(Building, col(Group.building_id) == Building.id)
            .order_by(Building.name, Group.name)
        )
        groups = session.exec(statement).all()
        for group in groups:
            group.classrooms.sort(key=lambda c: c.name)
        return list(groups)

    @staticmethod
    def create(*, input: GroupRegister, session: Session) -> Group:
        group = Group(
            name=input.name,
            building_id=input.building_id,
            main=input.main,
        )
        GroupRepository.__check_group_validation(
            group=group,
            building_id=input.building_id,
            classroom_ids=input.classroom_ids,
            session=session,
        )
        GroupRepository.__update_group_users(
            group=group,
            user_ids=input.user_ids,
            session=session,
        )
        return group

    @staticmethod
    def update(*, id: int, input: GroupUpdate, session: Session) -> Group:
        group = GroupRepository.get_by_id(id=id, session=session)
        group.name = input.name
        group.updated_at = datetime.now()

        GroupRepository.__check_group_validation(
            group=group,
            building_id=input.building_id,
            classroom_ids=input.classroom_ids,
            session=session,
        )

        old_users = group.user_ids_set()
        new_users = set(input.user_ids)
        users_ids_to_remove = old_users - new_users
        if len(new_users) > 0:
            GroupRepository.__update_group_users(
                group=group,
                user_ids=input.user_ids,
                session=session,
            )

        if len(users_ids_to_remove) > 0:
            users_to_remove = UserRepository.get_by_ids(
                ids=list(users_ids_to_remove), session=session
            )
            GroupRepository.__remove_users_from_group(
                group=group,
                users=users_to_remove,
                session=session,
            )
        session.add(group)
        return group

    @staticmethod
    def delete(*, id: int, session: Session) -> None:
        group = GroupRepository.get_by_id(id=id, session=session)
        GroupRepository.__remove_users_from_group(
            group=group,
            users=group.users,
            session=session,
        )
        session.delete(group)


class GroupNotFound(HTTPException):
    def __init__(self, info: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grupo com {info} não encontrado",
        )


class GroupWithoutClassroom(HTTPException):
    def __init__(self, group_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Grupo {group_name} não possui nenhuma sala",
        )


class GroupWithMultipleBuildings(HTTPException):
    def __init__(self, group_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Grupo {group_name} possui salas em mais de um prédio",
        )


class EditMainGroupClassrooms(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grupo principal não pode ter salas editadas",
        )


class GroupWithAllClassrooms(HTTPException):
    def __init__(self, building_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Apenas o grupo principal pode ter todas as salas do prédio {building_name}",
        )


class MainGroupIsUnique(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grupo principal já existe para este prédio",
        )


class MainGroupWithClassrooms(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grupo principal não pode ter salas em sua criação ou edição",
        )


class GroupAlreadyExists(HTTPException):
    def __init__(self, name: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Grupo com o nome {name} já existe",
        )
