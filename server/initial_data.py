import logging

from sqlmodel import Session, SQLModel, select

from server.config import CONFIG
from server.connections.db import engine
from server.models.database import (  # noqa
    building_db_model,
    user_building_link,
    user_db_model,
)
from server.models.http.requests.user_request_models import UserRegister
from server.repositories.users_repository import UserRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(session: Session) -> None:
    SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(user_db_model.User).where(
            user_db_model.User.username == CONFIG.first_superuser_username
        )
    ).first()
    if not user:
        user_in = UserRegister(
            name=CONFIG.first_superuser_name,
            username=CONFIG.first_superuser_username,
            email=CONFIG.first_superuser_email,
            cognito_id="123",
            is_admin=True,
        )
        user = UserRepository.create_user(session=session, user_in=user_in)


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
