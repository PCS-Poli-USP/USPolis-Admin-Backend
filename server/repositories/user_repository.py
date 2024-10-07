from sqlmodel import Session, col, select

from server.deps.cognito_client import ICognitoClient
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
    def get_by_username(*, username: str, session: Session) -> User:
        statement = select(User).where(col(User.username) == username)
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
        cognito_client: ICognitoClient,
    ) -> User:
        cognito_id = cognito_client.create_user(user_in.username, user_in.email)

        buildings = None
        if user_in.building_ids is not None:
            buildings = BuildingRepository.get_by_ids(
                ids=user_in.building_ids, session=session
            )

        new_user = User(
            name=user_in.name,
            username=user_in.username,
            email=user_in.email,
            is_admin=user_in.is_admin,
            cognito_id=cognito_id,
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
    def delete(
        *, user_id: int, session: Session, cognito_client: ICognitoClient
    ) -> None:
        user = UserRepository.get_by_id(user_id=user_id, session=session)
        session.delete(user)
        session.commit()
        cognito_client.delete_user(user.username)
