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
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.group_db_model import Group
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.models.http.requests.user_request_models import UserRegister
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.user_repository import UserRepository
from server.services.auth.auth_user_info import AuthUserInfo
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.class_model_factory import ClassModelFactory
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.model.subject_model_factory import SubjectModelFactory
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


def mock_authenticate(user: User, request: Request, session: SessionDep) -> User:
    request.state.current_user = user
    return user


@pytest.fixture(name="client")
def client_fixture(user: User, session: Session) -> Generator[TestClient, None, None]:
    """
    Admin client fixture, which is a TestClient with the mocked authentication and the mocked google authentication.
    """
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[google_authenticate] = mock_google_authenticate

    def _mock_authenticate(request: Request, session: SessionDep) -> User:
        return mock_authenticate(user, request, session)

    app.dependency_overrides[authenticate] = _mock_authenticate
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(name="restricted_client")
def restricted_client_fixture(
    restricted_user: User, session: Session
) -> Generator[TestClient, None, None]:
    """
    Restricted client fixture, which is a TestClient with a mocked restricted authentication and mocked google authentication.

    - The restricted user is a user that have the default admin and only have the default group of this building if you call the 'group' fixture.
    """
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[google_authenticate] = mock_google_authenticate

    def _mock_authenticate(request: Request, session: SessionDep) -> User:
        return mock_authenticate(restricted_user, request, session)

    app.dependency_overrides[authenticate] = _mock_authenticate
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(name="common_client")
def common_client_fixture(
    common_user: User, session: Session
) -> Generator[TestClient, None, None]:
    """
    Common client fixture, wich is a TestClient with the mocked common authentication and the mocked google authentication.

    - A common user is a user that not has a building and groups
    """
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[google_authenticate] = mock_google_authenticate

    def _mock_authenticate(request: Request, session: SessionDep) -> User:
        return mock_authenticate(common_user, request, session)

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
    """Fixture to create a standard building."""
    building = BuildingModelFactory(user, session).create_and_refresh()
    group = GroupModelFactory(building, session).create_and_refresh(classrooms=[])
    building.main_group = group
    session.add(building)
    session.commit()
    session.refresh(building)
    return building


@pytest.fixture(name="group")
def group_fixture(restricted_user: User, building: Building, session: Session) -> Group:
    """Fixture to create a standard main group for the standard building with a standard restricted user."""
    main_group = building.get_main_group()
    main_group.users.append(restricted_user)
    session.add(main_group)
    session.commit()
    session.refresh(main_group)
    return main_group


@pytest.fixture(name="classroom")
def classroom_fixture(
    user: User, building: Building, group: Group, session: Session
) -> Classroom:
    """Fixture to create a standard classroom in the standard main group that includes the starndard restricted user."""
    return ClassroomModelFactory(
        creator=user, building=building, group=group, session=session
    ).create_and_refresh()


@pytest.fixture(name="classrooms")
def classrooms_fixture(
    user: User, building: Building, group: Group, session: Session
) -> list[Classroom]:
    """Fixture to create a many classroom in the standard main group that includes the starndard restricted user."""
    return ClassroomModelFactory(
        creator=user, building=building, group=group, session=session
    ).create_many_and_refresh()


@pytest.fixture(name="allocated_classroom")
def allocated_classroom_fixture(
    user: User, building: Building, group: Group, class_: Class, session: Session
) -> Classroom:
    """Fixture to **create a classroom** in the default group of default building and **allocate the standard class in**.

    Keep in mind that this fixture will allocate the standard class, so make sure that you not use it at class allocation tests that uses the standard class.
    """
    classroom = ClassroomModelFactory(
        creator=user, building=building, group=group, session=session
    ).create_and_refresh()
    OccurrenceRepository.allocate_schedule(
        user=user, classroom=classroom, schedule=class_.schedules[0], session=session
    )
    session.commit()
    session.refresh(classroom)
    return classroom


@pytest.fixture(name="allocated_classrooms")
def allocated_classrooms_fixture(
    user: User, building: Building, subject: Subject, group: Group, session: Session
) -> tuple[list[Classroom], list[Class]]:
    """Fixture to **create many classrooms** in the default group of default building and **allocate the many classes in**.

    Keep in mind that this fixture will allocate the classes, so make sure that you not use it at class allocation tests.
    """
    classrooms = ClassroomModelFactory(
        creator=user, building=building, group=group, session=session
    ).create_many_and_refresh()
    classes = ClassModelFactory(
        subject=subject, session=session
    ).create_many_and_refresh()
    for i in range(len(classrooms)):
        OccurrenceRepository.allocate_schedule(
            user=user,
            classroom=classrooms[i],
            schedule=classes[i].schedules[0],
            session=session,
        )
        session.commit()
        session.refresh(classrooms[i])
    return classrooms, classes


@pytest.fixture(name="subject")
def subject_fixture(building: Building, session: Session) -> Subject:
    """Fixture to create a standard subject in the standard building."""
    return SubjectModelFactory(building=building, session=session).create_and_refresh()


@pytest.fixture(name="class_")
def class_fixture(subject: Subject, session: Session) -> Class:
    """Fixture to create a standard class in the standard subject.
    - **This class has only one schedule WITHOUT occurrences.**
    """
    return ClassModelFactory(subject=subject, session=session).create_and_refresh()


@pytest.fixture(name="classes")
def classes_fixture(subject: Subject, session: Session) -> list[Class]:
    """Fixture to create multiple standard classes in the standard subject.
    - **Each class has only one schedule WITHOU occurrences.**
    """
    return ClassModelFactory(subject=subject, session=session).create_many_and_refresh()
