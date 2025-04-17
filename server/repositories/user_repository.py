from datetime import datetime
from sqlmodel import Session, col, select

from server.models.database.user_building_link import UserBuildingLink
from server.models.database.user_db_model import User
from server.models.http.requests.user_request_models import UserRegister
from server.repositories.building_repository import BuildingRepository


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
    def create(
        *,
        creator: User | None,
        user_in: UserRegister,
        session: Session,
    ) -> User:
        """This commits, chage it later"""
        buildings = None
        if user_in.building_ids is not None:
            buildings = BuildingRepository.get_by_ids(
                ids=user_in.building_ids, session=session
            )

        new_user = User(
            name=user_in.name,
            email=user_in.email,
            is_admin=user_in.is_admin,
            created_by=creator,
            buildings=buildings or [],
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

    @staticmethod
    def update(*, user: User, session: Session) -> None:
        session.add(user)
        session.commit()

    @staticmethod
    def visit_user(
        *,
        user: User,
        session: Session,
    ) -> User:
        user.last_visited = datetime.now()
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
