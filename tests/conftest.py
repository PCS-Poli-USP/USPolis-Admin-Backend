from collections.abc import Generator
import os
from unittest.mock import MagicMock

from alembic import command
from alembic.config import Config
from pathlib import Path

from fastapi import Request
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel import Session, select
from server.config import CONFIG


# Import this to initialize the database
from server.db import (
    engine as db_engine,  # noqa: F401
    get_db,  # noqa: F401
)
from server.app import app
from server.deps.authenticate import authenticate, google_token_authenticate
from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.event_db_model import Event
from server.models.database.exam_db_model import Exam
from server.models.database.group_db_model import Group
from server.models.database.meeting_db_model import Meeting
from server.models.database.role_db_model import Role
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.models.http.requests.user_request_models import UserRegister
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.user_repository import UserRepository
from server.services.auth.auth_user_info import AuthUserInfo
from server.utils.enums.resources_enums import Resource
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.class_model_factory import ClassModelFactory
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.event_model_factory import EventModelFactory
from tests.factories.model.exam_model_factory import ExamModelFactory
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.model.meeting_model_factory import MeetingModelFactory
from tests.factories.base.base_factory import shared_faker
from tests.factories.model.role_model_factory import RoleModelFactory
from tests.factories.model.subject_model_factory import SubjectModelFactory
from tests.factories.model.user_model_factory import UserModelFactory

from tests.factories.base.base_factory import shared_faker

test_db_url = f"{CONFIG.test_db_uri}/{CONFIG.test_db_database}"
engine = create_engine(test_db_url)


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
def session_fixture() -> Generator[Session, None, None]:
    """Isolate each test in a transaction (with a SAVEPOINT so in-test
    `session.commit()` calls don't escape it) and roll it back afterwards,
    instead of truncating every table after every test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def _reset_faker_uniqueness() -> None:
    """Factories share one Faker instance so `.unique.xxx()` calls dedupe
    correctly within a test (see tests/factories/base/base_factory.py); clear
    its tracking between tests so small-cardinality providers don't get
    exhausted over the whole run — safe, since per-test rollback means no two
    tests' rows ever coexist for a reused "unique" value to actually collide."""
    shared_faker.unique.clear()


@pytest.fixture(name="mock_session")
def mock_session_fixture() -> MagicMock:
    return MagicMock()


def mock_google_authenticate() -> AuthUserInfo:
    return AuthUserInfo(
        email=CONFIG.mock_email,
        email_verified=True,
        domain="usp.br",
        name="Mock User",
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
    app.dependency_overrides[google_token_authenticate] = mock_google_authenticate

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
    app.dependency_overrides[google_token_authenticate] = mock_google_authenticate

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
    app.dependency_overrides[google_token_authenticate] = mock_google_authenticate

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
    return classroom


@pytest.fixture(name="subject")
def subject_fixture(building: Building, session: Session) -> Subject:
    """Fixture to create a standard subject in the standard building."""
    return SubjectModelFactory(building=building, session=session).create_and_refresh()


@pytest.fixture(name="class_")
def class_fixture(subject: Subject, session: Session) -> Class:
    """Fixture to create a standard class in the standard subject."""
    return ClassModelFactory(subject=subject, session=session).create_and_refresh()


@pytest.fixture(name="meeting")
def meeting_fixture(user: User, classroom: Classroom, session: Session) -> Meeting:
    """Fixture to create a standard meeting."""
    return MeetingModelFactory(
        classroom=classroom, creator=user, session=session
    ).create_and_refresh()


@pytest.fixture(name="exam")
def exam_fixture(
    user: User, classroom: Classroom, subject: Subject, session: Session
) -> Exam:
    """Fixture to create a standard exam (without classes)."""
    return ExamModelFactory(
        creator=user, classroom=classroom, subject=subject, session=session
    ).create_and_refresh()


@pytest.fixture(name="event")
def event_fixture(user: User, classroom: Classroom, session: Session) -> Event:
    """Fixture to create a standard event."""
    return EventModelFactory(
        classroom=classroom, creator=user, session=session
    ).create_and_refresh()


@pytest.fixture(name="role")
def role_fixture(session: Session) -> Role:
    """Fixture to create a standard role without any resource or permission."""
    return RoleModelFactory(
        session=session,
        resources=[Resource.BUILDING, Resource.CLASSROOM, Resource.COURSE],
    ).create_and_refresh()
