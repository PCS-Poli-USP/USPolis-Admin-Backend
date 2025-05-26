import logging

from sqlmodel import Session, select

from server.config import CONFIG
from server.db import engine
from server.models.database.user_db_model import User
from server.models.http.requests.user_request_models import UserRegister
from server.repositories.user_repository import UserRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(session: Session) -> None:
    user = session.exec(
        select(User).where(User.email == CONFIG.first_superuser_email)
    ).first()
    if not user:
        user_in = UserRegister(
            name=CONFIG.first_superuser_name,
            email=CONFIG.first_superuser_email,
            is_admin=True,
        )
        user = UserRepository.create(
            creator=None,
            session=session,
            input=user_in,
        )
        session.commit()
        session.refresh(user)


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
