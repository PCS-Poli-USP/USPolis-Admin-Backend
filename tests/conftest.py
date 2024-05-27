"""Pytest fixtures."""

from collections.abc import Generator

import pytest
from decouple import config  # type: ignore [import-untyped]
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.config import CONFIG

CONFIG.testing = True
CONFIG.override_auth = True
CONFIG.override_cognito_client = True
CONFIG.db_uri = config("TEST_DATABASE_URI")  # type: ignore
CONFIG.db_database = config("TEST_DATABASE_NAME", default="uspolis-test")  # type: ignore

# Override config settings before loading the app
from server.app import app  # noqa: E402
from server.models.database.building_db_model import Building  # noqa  # noqa
from server.models.database.user_db_model import User  # noqa
from server.repositories.users_repository import UserRepository  # noqa
from server.scripts.initial_data import init_db  # noqa


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    from server.db import engine  # noqa

    with Session(engine) as session:
        init_db(session)
        yield session
        # session.execute(delete(UserBuildingLink))
        # session.execute(delete(Building))
        # session.execute(delete(User))
        # session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=False)
def user(db: Session) -> Generator[User, None, None]:
    user = UserRepository.get_by_username(session=db, username=CONFIG.mock_username)
    yield user
