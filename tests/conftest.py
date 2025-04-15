from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlmodel import SQLModel, Session, select
from server.config import CONFIG


# Import this to initialize the database
from server.db import (
    engine as db_engine,  # noqa: F401
)
from server.app import app
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.models.http.requests.user_request_models import UserRegister
from server.repositories.user_repository import UserRepository
from tests.factories.model.building_model_factory import BuildingModelFactory

engine = create_engine(f"{CONFIG.test_db_uri}/{CONFIG.test_db_database}")

# create function to delete all data from tables and reset ids
with Session(engine) as session:
    statement = text("""
        CREATE OR REPLACE FUNCTION truncate_tables(username IN VARCHAR) RETURNS void AS $$
        DECLARE
            statements CURSOR FOR
                SELECT tablename FROM pg_tables
                WHERE tableowner = username AND schemaname = 'public';
        BEGIN
            -- Truncar as tabelas
            FOR stmt IN statements LOOP
                EXECUTE 'TRUNCATE TABLE ' || quote_ident(stmt.tablename) || ' RESTART IDENTITY' || ' CASCADE;';
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
    """)
    session.execute(statement)
    session.commit()


@pytest.fixture(name="session")
def session_fixture(request: pytest.FixtureRequest) -> Generator[Session, None, None]:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:

        def cleanup() -> None:
            # Clean-up após o teste (executa sempre, mesmo que o teste falhe)
            statement = text("SELECT truncate_tables('postgres');")
            session.execute(statement)
            session.commit()

        request.addfinalizer(cleanup)
        yield session


@pytest.fixture(name="mock_session")
def mock_session_fixture() -> MagicMock:
    return MagicMock()


@pytest.fixture(name="client")
def client_fixture() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(name="user")
def user_fixture(session: Session) -> Generator[User, None, None]:
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
            user_in=user_in,
        )
    user = UserRepository.get_by_email(session=session, email=CONFIG.mock_email)
    yield user


@pytest.fixture(name="building")
def building_fixture(user: User, session: Session) -> Building:
    return BuildingModelFactory(user, session).create_and_refresh()
