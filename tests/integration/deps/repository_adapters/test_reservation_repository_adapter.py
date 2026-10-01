import pytest
from sqlmodel import Session

from server.deps.interval_dep import QueryInterval
from server.deps.owned_building_ids import owned_building_ids
from server.deps.repository_adapters.reservation_repository_adapter import (
    ReservationRespositoryAdapter,
)
from server.models.database.classroom_db_model import Classroom
from server.models.database.meeting_db_model import Meeting
from server.models.database.reservation_db_model import Reservation
from server.models.database.user_db_model import User
from server.services.security.classrooms_permission_checker import (
    ForbiddenClassroomAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import ClassroomAction
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from tests.factories.request.reservation_request_factory import (
    ReservationRequestFactory,
)
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _adapter(*, user: User, session: Session) -> ReservationRespositoryAdapter:
    return ReservationRespositoryAdapter(
        owned_building_ids=owned_building_ids(user=user, session=session),
        session=session,
        user=user,
        interval=QueryInterval(),
        permission_index=build_permission_index(user),
    )


def _with_classroom(meeting: Meeting, classroom: Classroom, session: Session) -> Reservation:
    # MeetingModelFactory/ReservationModelFactory never actually wire the
    # classroom they're given onto the created schedule, so the fixture
    # reservation has no classroom until wired explicitly here.
    meeting.reservation.schedule.classroom = classroom
    session.add(meeting.reservation.schedule)
    session.commit()
    return meeting.reservation


class TestGetAll:
    def test_admin_sees_every_reservation(
        self,
        admin_user: User,
        meeting: Meeting,
        classroom: Classroom,
        session: Session,
    ) -> None:
        reservation = _with_classroom(meeting, classroom, session)
        adapter = _adapter(user=admin_user, session=session)

        reservations = adapter.get_all()

        assert reservation.id in [r.id for r in reservations]

    def test_restricted_user_sees_reservations_of_owned_classrooms(
        self,
        restricted_user: User,
        meeting: Meeting,
        classroom: Classroom,
        session: Session,
    ) -> None:
        reservation = _with_classroom(meeting, classroom, session)
        adapter = _adapter(user=restricted_user, session=session)

        reservations = adapter.get_all()

        assert reservation.id in [r.id for r in reservations]

    def test_common_user_sees_none(
        self,
        common_user: User,
        meeting: Meeting,
        classroom: Classroom,
        session: Session,
    ) -> None:
        reservation = _with_classroom(meeting, classroom, session)
        adapter = _adapter(user=common_user, session=session)

        assert reservation.id not in [r.id for r in adapter.get_all()]


class TestGetById:
    def test_denies_without_permission(
        self,
        common_user: User,
        meeting: Meeting,
        classroom: Classroom,
        session: Session,
    ) -> None:
        reservation = _with_classroom(meeting, classroom, session)
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.get_by_id(must_be_int(reservation.id))

    def test_allows_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        meeting: Meeting,
        classroom: Classroom,
        session: Session,
    ) -> None:
        reservation = _with_classroom(meeting, classroom, session)
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)

        found = adapter.get_by_id(must_be_int(reservation.id))

        assert found.id == reservation.id


class TestCreate:
    def test_denies_without_permission(
        self, common_user: User, classroom: Classroom, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        input = ReservationRequestFactory(
            reservation_type=ReservationType.MEETING, classroom=classroom
        ).create_input()

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.create(input)

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
        input = ReservationRequestFactory(
            reservation_type=ReservationType.MEETING, classroom=classroom
        ).create_input()

        created = adapter.create(input)

        assert created.title == input.title


class TestUpdate:
    def test_denies_without_permission(
        self,
        common_user: User,
        meeting: Meeting,
        classroom: Classroom,
        session: Session,
    ) -> None:
        reservation = _with_classroom(meeting, classroom, session)
        adapter = _adapter(user=common_user, session=session)
        input = ReservationRequestFactory(
            reservation_type=ReservationType.MEETING, classroom=classroom
        ).update_input()

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.update(must_be_int(reservation.id), input)

    def test_updates_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        meeting: Meeting,
        classroom: Classroom,
        session: Session,
    ) -> None:
        reservation = _with_classroom(meeting, classroom, session)
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.RESERVE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        input = ReservationRequestFactory(
            reservation_type=ReservationType.MEETING, classroom=classroom
        ).update_input(title="Nova Reserva")

        updated = adapter.update(must_be_int(reservation.id), input)

        assert updated.title == "Nova Reserva"


class TestDelete:
    def test_denies_without_permission(
        self,
        common_user: User,
        meeting: Meeting,
        classroom: Classroom,
        session: Session,
    ) -> None:
        reservation = _with_classroom(meeting, classroom, session)
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.delete(must_be_int(reservation.id))

    def test_deletes_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        meeting: Meeting,
        classroom: Classroom,
        session: Session,
    ) -> None:
        reservation = _with_classroom(meeting, classroom, session)
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.RESERVE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        reservation_id = must_be_int(reservation.id)

        adapter.delete(reservation_id)
        session.commit()

        assert session.get(Reservation, reservation_id) is None
