"""Who is emailed about a solicitation (solicitation_recipients.py): whoever
can approve or deny it, through a role or a legacy group.

A solicitation for a classroom goes to whoever holds RESERVE on that classroom
(directly or through its building). One with no classroom goes to whoever
holds RESERVE on its building or on any classroom of it: the same people who
see it in the inbox.
"""

from collections.abc import Sequence
from unittest.mock import AsyncMock, patch

from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.solicitation_db_model import Solicitation
from server.models.database.user_db_model import User
from server.repositories.solicitation_repository import SolicitationRepository
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.must_be_int import must_be_int
from tests.api.roles.conftest import ALL_RESOURCES, Grants
from tests.api.roles.world import World
from tests.factories.model.user_model_factory import UserModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _user(session: Session, receive_emails: bool = True) -> User:
    return UserModelFactory(session=session).create_and_refresh(
        is_admin=False, receive_emails=receive_emails
    )


def _with_classroom_role(
    w: World, classroom: Classroom | None, actions: Sequence[ClassroomAction]
) -> User:
    user = _user(w.session)
    RolePermissionTestHelper.grant_classroom_permission(
        user=user,
        resource_id=ALL_RESOURCES if classroom is None else must_be_int(classroom.id),
        actions=actions,
        granted_by=w.admin,
        session=w.session,
    )
    return user


def _with_building_role(w: World, building: Building) -> User:
    user = _user(w.session)
    RolePermissionTestHelper.grant_building_permission(
        user=user,
        resource_id=must_be_int(building.id),
        actions=[BuildingAction.RESERVE],
        granted_by=w.admin,
        session=w.session,
    )
    return user


def _recipients(solicitation: Solicitation) -> set[int]:
    return {
        must_be_int(u.id) for u in solicitation.get_administrative_users_for_email()
    }


def _id(user: User) -> int:
    return must_be_int(user.id)


class TestForAClassroom:
    """The solicitation names a classroom: whoever reserves that classroom."""

    def test_reserve_on_the_classroom_or_its_building(
        self, world: World, classroom_a2: Classroom
    ) -> None:
        on_classroom = _with_classroom_role(
            world, world.classroom_a, [ClassroomAction.RESERVE]
        )
        on_building = _with_building_role(world, world.building_a)
        on_sibling = _with_classroom_role(
            world, classroom_a2, [ClassroomAction.RESERVE]
        )

        recipients = _recipients(world.solicitation())

        assert {_id(on_classroom), _id(on_building)} <= recipients
        assert _id(on_sibling) not in recipients

    def test_not_who_cannot_approve_it(self, world: World) -> None:
        other_building = _with_classroom_role(
            world, world.classroom_b, [ClassroomAction.RESERVE]
        )
        read_only = _with_classroom_role(
            world, world.classroom_a, [ClassroomAction.READ]
        )
        wildcard = _with_classroom_role(world, None, [ClassroomAction.RESERVE])

        recipients = _recipients(world.solicitation())

        assert not {_id(other_building), _id(read_only), _id(wildcard)} & recipients

    def test_only_who_wants_emails(self, world: World) -> None:
        user = _user(world.session, receive_emails=False)
        RolePermissionTestHelper.grant_classroom_permission(
            user=user,
            resource_id=must_be_int(world.classroom_a.id),
            actions=[ClassroomAction.RESERVE],
            granted_by=world.admin,
            session=world.session,
        )

        assert _id(user) not in _recipients(world.solicitation())

    def test_legacy_group_members_too(
        self, world: World, role_user: User, grant: Grants
    ) -> None:
        grant.legacy_group(world.building_a)

        assert _id(role_user) in _recipients(world.solicitation())

    def test_an_admin_only_through_a_role_or_group(self, world: World) -> None:
        # admin_user is in no group of building A and has no role there.
        assert _id(world.admin) not in _recipients(world.solicitation())


class TestForABuilding:
    """No classroom asked for: whoever reserves the building or any classroom
    of it (the inbox rule)."""

    def test_reserve_on_the_building_or_any_of_its_classrooms(
        self, world: World, classroom_a2: Classroom
    ) -> None:
        on_classroom = _with_classroom_role(
            world, world.classroom_a, [ClassroomAction.RESERVE]
        )
        on_sibling = _with_classroom_role(
            world, classroom_a2, [ClassroomAction.RESERVE]
        )
        on_building = _with_building_role(world, world.building_a)
        other_building = _with_building_role(world, world.building_b)

        recipients = _recipients(world.solicitation(with_classroom=False))

        assert {_id(on_classroom), _id(on_sibling), _id(on_building)} <= recipients
        assert _id(other_building) not in recipients


class TestAllocatedSolicitation:
    def test_reserve_on_its_classroom(
        self, world: World, classroom_a2: Classroom, session: Session
    ) -> None:
        on_classroom = _with_classroom_role(
            world, world.classroom_a, [ClassroomAction.RESERVE]
        )
        on_building = _with_building_role(world, world.building_a)
        on_sibling = _with_classroom_role(
            world, classroom_a2, [ClassroomAction.RESERVE]
        )
        solicitation = SolicitationRepository.approve(
            id=must_be_int(world.solicitation().id),
            classroom_id=must_be_int(world.classroom_a.id),
            user=world.admin,
            session=session,
        )
        session.commit()
        session.refresh(solicitation)

        recipients = _recipients(solicitation)

        assert {_id(on_classroom), _id(on_building)} <= recipients
        assert _id(on_sibling) not in recipients


def test_requesting_emails_the_role_holders(
    world: World, role_client: TestClient
) -> None:
    reserver = _with_classroom_role(world, world.classroom_a, [ClassroomAction.RESERVE])
    send = AsyncMock()

    with patch(
        "server.services.email.email_service.EmailService.send_solicitation_request_email",
        send,
    ):
        response = role_client.post(
            "/solicitations",
            json=jsonable_encoder(world.solicitation_input(world.classroom_a)),
        )

    assert response.status_code == 200, response.text
    users = send.call_args.args[0]
    assert _id(reserver) in {_id(u) for u in users}
