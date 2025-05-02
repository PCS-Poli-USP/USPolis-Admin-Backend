from collections.abc import Generator
import os
from unittest.mock import MagicMock

from alembic import command
from alembic.config import Config
from pathlib import Path

from fastapi import Request
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlmodel import Session, select
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
from tests.factories.model.user_model_factory import UserModelFactory

test_db_url = f"{CONFIG.test_db_uri}/{CONFIG.test_db_database}"
engine = create_engine(test_db_url)

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
                IF stmt.tablename != 'alembic_version' THEN
                    EXECUTE 'TRUNCATE TABLE ' || quote_ident(stmt.tablename) || ' RESTART IDENTITY' || ' CASCADE;';
                END IF;
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
    """)
    session.execute(statement)
    session.commit()


def run_alembic_migrations() -> None:
    alembic_cfg = Config(str(Path(__file__).parent.parent / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", "migrations")
    os.environ["ALEMBIC_URL"] = CONFIG.test_alembic_url
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> Generator[None, None, None]:
    run_alembic_migrations()
    yield


@pytest.fixture(name="session")
def session_fixture(request: pytest.FixtureRequest) -> Generator[Session, None, None]:
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
        email=CONFIG.mock_email,
        name="Mock User",
        email_verified=True,
        picture="",
        given_name="Mock",
        family_name="User",
    )


def mock_authenticate(request: Request, session: SessionDep) -> User:
    user = session.exec(
        select(User).where(User.email == CONFIG.first_superuser_email)
    ).first()
    if not user:
        raise Exception("Mocked user not found")
    request.state.current_user = user
    return user


def mock_restricted_authenticate(
    restricted_user: User, request: Request, session: SessionDep
) -> User:
    request.state.current_user = restricted_user
    return restricted_user


def mock_common_authenticate(
    common: User, request: Request, session: SessionDep
) -> User:
    request.state.current_user = common
    return common


# This user call user fixture that creates the mocked user
@pytest.fixture(name="client")
def client_fixture(user: User, session: Session) -> Generator[TestClient, None, None]:
    """
    Admin client fixture, wich is a TestClient with the mocked authentication (admin user)
    and the mocked google authentication.
    """
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[google_authenticate] = mock_google_authenticate
    app.dependency_overrides[authenticate] = mock_authenticate
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(name="restricted_client")
def restricted_client_fixture(
    restricted_user: User, session: Session
) -> Generator[TestClient, None, None]:
    """
    Admin client fixture, wich is a TestClient with the mocked authentication (admin user)
    and the mocked google authentication.
    """
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[google_authenticate] = mock_google_authenticate

    def _mock_authenticate(request: Request, session: SessionDep) -> User:
        return mock_restricted_authenticate(restricted_user, request, session)

    app.dependency_overrides[authenticate] = _mock_authenticate
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(name="common_client")
def common_client_fixture(
    common_user: User, session: Session
) -> Generator[TestClient, None, None]:
    """
    Admin client fixture, wich is a TestClient with the mocked authentication (admin user)
    and the mocked google authentication.
    """
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[google_authenticate] = mock_google_authenticate

    def _mock_authenticate(request: Request, session: SessionDep) -> User:
        return mock_common_authenticate(common_user, request, session)

    app.dependency_overrides[authenticate] = _mock_authenticate
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(name="public_client")
def public_client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Public client or client without authetication overrides.
    """
    app.dependency_overrides[get_db] = lambda: session
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
            input=user_in,
        )
        session.commit()
        session.refresh(user)
    yield user


@pytest.fixture(name="restricted_user")
def restricted_user_fixture(
    building: Building, session: Session
) -> Generator[User, None, None]:
    user = UserModelFactory(session=session).create_and_refresh(
        is_admin=False,
        buildings=[building],
    )
    yield user


@pytest.fixture(name="common_user")
def common_user_fixture(session: Session) -> Generator[User, None, None]:
    user = UserModelFactory(session=session).create_and_refresh(
        is_admin=False,
    )
    yield user


@pytest.fixture(name="building")
def building_fixture(user: User, session: Session) -> Building:
    return BuildingModelFactory(user, session).create_and_refresh()
