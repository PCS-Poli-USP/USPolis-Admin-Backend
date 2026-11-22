"""Fixtures for the role-only suite.

Every test here runs as `role_user`: a user with no group and no
`user.buildings`, whose access comes only from roles. Two buildings exist (A and
B), so each test can check both that a grant works and that it does not leak to
the other building. Grant permissions with the `grant` fixture.
"""

from collections.abc import Generator, Sequence
from dataclasses import dataclass

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.app import app
from server.db import get_db
from server.deps.authenticate import authenticate, google_token_authenticate
from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.must_be_int import must_be_int
from tests.api.roles.world import World
from tests.conftest import mock_authenticate, mock_google_authenticate
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.class_model_factory import ClassModelFactory
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.model.subject_model_factory import SubjectModelFactory
from tests.factories.model.user_model_factory import UserModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper

ALL_RESOURCES = -1


@pytest.fixture(name="role_user")
def role_user_fixture(session: Session) -> User:
    """A non-admin user with no group: access only through roles."""
    user = UserModelFactory(session=session).create_and_refresh(is_admin=False)
    assert not user.groups and not user.buildings and not user.roles
    return user


@pytest.fixture(name="role_client")
def role_client_fixture(
    role_user: User, session: Session
) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[google_token_authenticate] = mock_google_authenticate

    def _mock_authenticate(request: Request, session: SessionDep) -> User:
        return mock_authenticate(role_user, request, session)

    app.dependency_overrides[authenticate] = _mock_authenticate
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _building_with_main_group(admin_user: User, session: Session) -> Building:
    building = BuildingModelFactory(admin_user, session).create_and_refresh()
    building.main_group = GroupModelFactory(building, session).create_and_refresh(
        classrooms=[]
    )
    session.add(building)
    session.commit()
    session.refresh(building)
    return building


@pytest.fixture(name="building_a")
def building_a_fixture(admin_user: User, session: Session) -> Building:
    return _building_with_main_group(admin_user, session)


@pytest.fixture(name="building_b")
def building_b_fixture(admin_user: User, session: Session) -> Building:
    return _building_with_main_group(admin_user, session)


def _classroom(admin_user: User, building: Building, session: Session) -> Classroom:
    return ClassroomModelFactory(
        creator=admin_user, building=building, session=session
    ).create_and_refresh()


@pytest.fixture(name="classroom_a")
def classroom_a_fixture(
    admin_user: User, building_a: Building, session: Session
) -> Classroom:
    return _classroom(admin_user, building_a, session)


@pytest.fixture(name="classroom_a2")
def classroom_a2_fixture(
    admin_user: User, building_a: Building, session: Session
) -> Classroom:
    """A second classroom in building A, for classroom-level grants."""
    return _classroom(admin_user, building_a, session)


@pytest.fixture(name="classroom_b")
def classroom_b_fixture(
    admin_user: User, building_b: Building, session: Session
) -> Classroom:
    return _classroom(admin_user, building_b, session)


@pytest.fixture(name="subject_a")
def subject_a_fixture(building_a: Building, session: Session) -> Subject:
    return SubjectModelFactory(
        building=building_a, session=session
    ).create_and_refresh()


@pytest.fixture(name="subject_b")
def subject_b_fixture(building_b: Building, session: Session) -> Subject:
    return SubjectModelFactory(
        building=building_b, session=session
    ).create_and_refresh()


@pytest.fixture(name="class_a")
def class_a_fixture(subject_a: Subject, session: Session) -> Class:
    return ClassModelFactory(subject=subject_a, session=session).create_and_refresh()


@pytest.fixture(name="class_b")
def class_b_fixture(subject_b: Subject, session: Session) -> Class:
    return ClassModelFactory(subject=subject_b, session=session).create_and_refresh()


@dataclass
class Grants:
    """Grant `role_user` permissions through roles (one role per call)."""

    user: User
    admin: User
    session: Session

    def building(
        self, building: Building | None, actions: Sequence[BuildingAction]
    ) -> None:
        """Grant `actions` on `building`, or on every building when None."""
        RolePermissionTestHelper.grant_building_permission(
            user=self.user,
            resource_id=ALL_RESOURCES if building is None else must_be_int(building.id),
            actions=actions,
            granted_by=self.admin,
            session=self.session,
        )

    def classroom(
        self, classroom: Classroom | None, actions: Sequence[ClassroomAction]
    ) -> None:
        """Grant `actions` on `classroom`, or on every classroom when None."""
        RolePermissionTestHelper.grant_classroom_permission(
            user=self.user,
            resource_id=ALL_RESOURCES
            if classroom is None
            else must_be_int(classroom.id),
            actions=actions,
            granted_by=self.admin,
            session=self.session,
        )

    def legacy_group(self, building: Building) -> None:
        """Make the user a member of `building`'s main group (the legacy
        model: everything in the building, no role)."""
        main_group = building.get_main_group()
        main_group.users.append(self.user)
        self.user.buildings = [building]
        self.session.add_all([main_group, self.user])
        self.session.commit()
        self.session.refresh(self.user)


@pytest.fixture(name="grant")
def grant_fixture(role_user: User, admin_user: User, session: Session) -> Grants:
    return Grants(user=role_user, admin=admin_user, session=session)


@pytest.fixture(name="world")
def world_fixture(
    session: Session,
    admin_user: User,
    building_a: Building,
    building_b: Building,
    classroom_a: Classroom,
    classroom_b: Classroom,
    subject_a: Subject,
    subject_b: Subject,
    class_a: Class,
    class_b: Class,
) -> World:
    return World(
        session=session,
        admin=admin_user,
        building_a=building_a,
        building_b=building_b,
        classroom_a=classroom_a,
        classroom_b=classroom_b,
        subject_a=subject_a,
        subject_b=subject_b,
        class_a=class_a,
        class_b=class_b,
        target=classroom_a,
    )
