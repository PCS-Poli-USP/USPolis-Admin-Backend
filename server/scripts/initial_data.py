import logging

from sqlmodel import Session, SQLModel, select

from server.config import CONFIG
from server.db import engine
from server.mocks.services.cognito_client_mock import CognitoClientMock

from server.models.database import (  # noqa
    building_db_model,
    user_building_link,
    user_db_model,
    subject_db_model,
    subject_building_link,
    classroom_db_model,
    holiday_category_db_model,
    holiday_db_model,
    calendar_db_model,
    calendar_holiday_category_link,
    institutional_event_db_model,
)
from server.models.database.user_db_model import User
from server.models.http.requests.user_request_models import UserRegister
from server.repositories.users_repository import UserRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(session: Session) -> None:
    SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.username == CONFIG.first_superuser_username)
    ).first()
    if not user:
        user_in = UserRegister(
            name=CONFIG.first_superuser_name,
            username=CONFIG.first_superuser_username,
            email=CONFIG.first_superuser_email,
            is_admin=True,
        )
        user = UserRepository.create(
            creator=None,
            cognito_client=CognitoClientMock(),
            session=session,
            user_in=user_in,
        )


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
