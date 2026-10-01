import pytest
from sqlmodel import Session

from server.deps.repository_adapters.meeting_repository_adapter import (
    MeetingRepositoryAdapter,
)
from server.models.database.classroom_db_model import Classroom
from server.models.database.meeting_db_model import Meeting
from server.models.database.user_db_model import User
from server.services.security.classrooms_permission_checker import (
    ForbiddenClassroomAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import ClassroomAction
from server.utils.must_be_int import must_be_int
from tests.factories.request.meeting_request_factory import MeetingRequestFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _adapter(*, user: User, session: Session) -> MeetingRepositoryAdapter:
    return MeetingRepositoryAdapter(
        user=user,
        session=session,
        permission_index=build_permission_index(user),
    )


class TestGetById:
    def test_denies_without_permission(
        self, common_user: User, classroom: Classroom, meeting: Meeting, session: Session
    ) -> None:
        # MeetingModelFactory/ReservationModelFactory never actually wire the
        # classroom they're given onto the created schedule, so the fixture
        # meeting has no classroom - required for the permission checker to
        # resolve via the classroom rather than crashing on get_building().
        meeting.reservation.schedule.classroom = classroom
        session.add(meeting.reservation.schedule)
        session.commit()
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.get_by_id(must_be_int(meeting.id))

    def test_allows_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        classroom: Classroom,
        meeting: Meeting,
        session: Session,
    ) -> None:
        meeting.reservation.schedule.classroom = classroom
        session.add(meeting.reservation.schedule)
        session.commit()
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)

        found = adapter.get_by_id(must_be_int(meeting.id))

        assert found.id == meeting.id


class TestCreate:
    def test_denies_without_permission(
        self, common_user: User, classroom: Classroom, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        input = MeetingRequestFactory(classroom=classroom).create_input()

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.create(common_user, input)

    def test_creates_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        classroom: Classroom,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.RESERVE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        input = MeetingRequestFactory(classroom=classroom).create_input()

        created = adapter.create(common_user, input)

        assert created.reservation.title == input.title


class TestUpdate:
    def test_denies_without_permission(
        self, common_user: User, classroom: Classroom, meeting: Meeting, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        input = MeetingRequestFactory(classroom=classroom).update_input()

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.update(must_be_int(meeting.id), input)

    def test_updates_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        classroom: Classroom,
        meeting: Meeting,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.RESERVE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        input = MeetingRequestFactory(classroom=classroom).update_input(
            title="Nova Reunião"
        )

        updated = adapter.update(must_be_int(meeting.id), input)

        assert updated.reservation.title == "Nova Reunião"
