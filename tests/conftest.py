from collections.abc import Generator
from unittest.mock import MagicMock

from fastapi import Request
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlmodel import SQLModel, Session, select
from server.config import CONFIG


# Import this to initialize the database
from server.db import (
    engine as db_engine,  # noqa: F401
    get_db,  # noqa: F401
)
from server.app import app
from server.deps.authenticate import authenticate, google_authenticate
from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User
from server.models.http.requests.user_request_models import UserRegister
from server.repositories.user_repository import UserRepository
from server.services.auth.auth_user_info import AuthUserInfo
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


def mock_google_authenticate() -> AuthUserInfo:
    return AuthUserInfo(
        email=CONFIG.mock_email, name="Test User", email_verified=True, picture=""
    )


def mock_authenticate(request: Request, session: SessionDep) -> User:
    user = session.exec(
        select(User).where(User.email == CONFIG.first_superuser_email)
    ).first()
    if not user:
        raise Exception("Mocked user not found")
    request.state.current_user = user
    return user


# This user call user fixture that creates the mocked user
@pytest.fixture(name="client")
def client_fixture(user: User, session: Session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[google_authenticate] = mock_google_authenticate
    app.dependency_overrides[authenticate] = mock_authenticate
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


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
    yield user


@pytest.fixture(name="building")
def building_fixture(user: User, session: Session) -> Building:
    return BuildingModelFactory(user, session).create_and_refresh()
