"""Pytest fixtures."""

from collections.abc import Generator

import pytest
from decouple import config  # type: ignore [import-untyped]
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from server.config import CONFIG

CONFIG.testing = True
CONFIG.override_auth = True
CONFIG.override_cognito_client = True
CONFIG.db_uri = config("TEST_DATABASE_URI")  # type: ignore
CONFIG.db_database = config("TEST_DATABASE_NAME", default="uspolis-test")  # type: ignore

from server.app import app  # noqa
from server.models.database.building_db_model import Building  # noqa  # noqa
from server.models.database.user_db_model import User  # noqa
from server.repositories.user_repository import UserRepository  # noqa
from server.scripts.initial_data import init_db  # noqa
from server.db import engine  # noqa

# create function to delete all data from tables
with Session(engine) as session:
    statement = text("""
    CREATE OR REPLACE FUNCTION truncate_tables(username IN VARCHAR) RETURNS void AS $$
    DECLARE
        statements CURSOR FOR
            SELECT tablename FROM pg_tables
            WHERE tableowner = username AND schemaname = 'public';
    BEGIN
        FOR stmt IN statements LOOP
            EXECUTE 'TRUNCATE TABLE ' || quote_ident(stmt.tablename) || ' CASCADE;';
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;
    """)
    session.execute(statement)
    session.commit()


@pytest.fixture(autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = text("SELECT truncate_tables('postgres');")
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=False)
def user(db: Session) -> Generator[User, None, None]:
    user = UserRepository.get_by_username(session=db, username=CONFIG.mock_username)
    yield user
