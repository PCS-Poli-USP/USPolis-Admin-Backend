from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from server.models.database.building_db_model import Building
from server.models.database.user_building_link import UserBuildingLink
from server.models.database.user_db_model import User
from server.models.http.requests.user_request_models import UserRegister, UserUpdate
from server.utils.brazil_datetime import BrazilDatetime


class UserRepository:
    @staticmethod
    def get_by_id(*, user_id: int, session: Session) -> User:
        statement = select(User).where(col(User.id) == user_id)
        user = session.exec(statement).one()
        return user

    @staticmethod
    def get_by_ids(*, ids: list[int], session: Session) -> list[User]:
        statement = select(User).where(col(User.id).in_(ids))
        users = session.exec(statement).all()
        return list(users)

    @staticmethod
    def get_by_email(*, email: str, session: Session) -> User:
        statement = select(User).where(col(User.email) == email)
        user = session.exec(statement).one()
        return user

    @staticmethod
    def get_all(*, session: Session) -> list[User]:
        statement = select(User)
        users = session.exec(statement).all()
        return list(users)

    @staticmethod
    def get_all_on_building(*, building_id: int, session: Session) -> list[User]:
        statement = (
            select(User)
            .join(UserBuildingLink)
            .where(UserBuildingLink.building_id == building_id)
        )
        users = session.exec(statement).all()
        return list(users)

    @staticmethod
    def __update_user_groups(
        *, user: User, group_ids: list[int], session: Session
    ) -> None:
        """Update user groups, keeping correctly the users buildings defined by his groups.\n"""
        from server.repositories.group_repository import GroupRepository

        buildings_set: set[Building] = set()
        if group_ids:
            groups = GroupRepository.get_by_ids(ids=group_ids, session=session)
            for group in groups:
                buildings_set.add(group.building)
            user.buildings = list(buildings_set)
            user.groups = groups
        else:
            user.groups = []
            user.buildings = []

    @staticmethod
    def create(
        *,
        creator: User | None,
        input: UserRegister,
        session: Session,
    ) -> User:
        new_user = User(
            name=input.name,
            email=input.email,
            is_admin=input.is_admin,
            created_by=creator,
        )
        UserRepository.__update_user_groups(
            user=new_user,
            group_ids=input.group_ids,
            session=session,
        )
        session.add(new_user)
        return new_user

    @staticmethod
    def update(
        *, requester: User, id: int, input: UserUpdate, session: Session
    ) -> User:
        user_to_update = UserRepository.get_by_id(user_id=id, session=session)

        if id == requester.id:
            if requester.is_admin != input.is_admin:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    "Não pode editar seu próprio status de admin",
                )

        UserRepository.__update_user_groups(
            user=user_to_update,
            group_ids=input.group_ids,
            session=session,
        )
        user_to_update.is_admin = input.is_admin
        user_to_update.updated_at = BrazilDatetime.now_utc()
        session.add(user_to_update)
        return user_to_update

    @staticmethod
    def visit_user(
        *,
        user: User,
        session: Session,
    ) -> User:
        user.last_visited = BrazilDatetime.now_utc()
        session.add(user)
        return user

    @staticmethod
    def delete(
        *,
        user_id: int,
        session: Session,
    ) -> None:
        user = UserRepository.get_by_id(user_id=user_id, session=session)
        session.delete(user)
        session.commit()
