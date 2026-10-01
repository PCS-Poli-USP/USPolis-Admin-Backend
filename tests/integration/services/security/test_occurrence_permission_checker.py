from datetime import date, time

import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.group_db_model import Group
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.user_db_model import User
from server.services.security.classrooms_permission_checker import (
    ForbiddenClassroomAccess,
)
from server.services.security.occurrence_permission_checker import (
    OccurrencePermissionChecker,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.services.security.schedule_permission_checker import (
    ForbiddenScheduleAccess,
)
from server.utils.enums.actions_enums import ClassroomAction
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.schedule_model_factory import ScheduleModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _make_occurrence_with_classroom(
    *, classroom: Classroom, class_: Class, session: Session
) -> Occurrence:
    schedule = ScheduleModelFactory(session=session, class_=class_).create_and_refresh()
    occurrence = Occurrence(
        start_time=time(8, 0),
        end_time=time(10, 0),
        date=date.today(),
        classroom_id=must_be_int(classroom.id),
        schedule_id=must_be_int(schedule.id),
    )
    session.add(occurrence)
    session.commit()
    session.refresh(occurrence)
    return occurrence


def _make_unallocated_occurrence(*, class_: Class, session: Session) -> Occurrence:
    schedule = ScheduleModelFactory(session=session, class_=class_).create_and_refresh()
    occurrence = Occurrence(
        start_time=time(8, 0),
        end_time=time(10, 0),
        date=date.today(),
        classroom_id=None,
        schedule_id=must_be_int(schedule.id),
    )
    session.add(occurrence)
    session.commit()
    session.refresh(occurrence)
    return occurrence


def test_occurrence_checker_admin_bypasses(
    classroom: Classroom, class_: Class, admin_user: User, session: Session
) -> None:
    occurrence = _make_occurrence_with_classroom(
        classroom=classroom, class_=class_, session=session
    )
    checker = OccurrencePermissionChecker(
        user=admin_user,
        session=session,
        permission_index=build_permission_index(admin_user),
    )
    checker.check_permission(occurrence, ClassroomAction.READ)


def test_occurrence_checker_with_classroom_denies_without_permission(
    classroom: Classroom, class_: Class, common_user: User, session: Session
) -> None:
    occurrence = _make_occurrence_with_classroom(
        classroom=classroom, class_=class_, session=session
    )
    checker = OccurrencePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(occurrence, ClassroomAction.READ)


def test_occurrence_checker_with_classroom_allows_via_classroom_permission(
    classroom: Classroom,
    class_: Class,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    occurrence = _make_occurrence_with_classroom(
        classroom=classroom, class_=class_, session=session
    )
    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = OccurrencePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(occurrence, ClassroomAction.READ)


def test_occurrence_checker_with_classroom_allows_via_wildcard_permission(
    classroom: Classroom,
    class_: Class,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    occurrence = _make_occurrence_with_classroom(
        classroom=classroom, class_=class_, session=session
    )
    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=-1,
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = OccurrencePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(occurrence, ClassroomAction.READ)


def test_occurrence_checker_without_classroom_falls_back_to_schedule(
    class_: Class, common_user: User, session: Session
) -> None:
    """No classroom on the occurrence -> delegates to SchedulePermissionChecker via
    the schedule's class_/subject/buildings, not the ClassroomPermissionChecker."""
    occurrence = _make_unallocated_occurrence(class_=class_, session=session)

    checker = OccurrencePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenScheduleAccess):
        checker.check_permission(occurrence, ClassroomAction.READ)


def test_occurrence_checker_id_dispatch_matches_object_dispatch(
    classroom: Classroom, class_: Class, common_user: User, session: Session
) -> None:
    occurrence = _make_occurrence_with_classroom(
        classroom=classroom, class_=class_, session=session
    )
    checker = OccurrencePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(must_be_int(occurrence.id), ClassroomAction.READ)


def test_occurrence_checker_list_denies_when_any_occurrence_disallowed(
    classroom: Classroom,
    building: Building,
    group: Group,
    class_: Class,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    """Grants access to `classroom` only, so occurrence_a is individually
    allowed while occurrence_b (a different, ungranted classroom) is not -
    proving the list check evaluates every item rather than short-circuiting
    once it finds one allowed entry."""
    other_classroom = ClassroomModelFactory(
        creator=admin_user, building=building, group=group, session=session
    ).create_and_refresh()
    occurrence_a = _make_occurrence_with_classroom(
        classroom=classroom, class_=class_, session=session
    )
    occurrence_b = _make_occurrence_with_classroom(
        classroom=other_classroom, class_=class_, session=session
    )
    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = OccurrencePermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission([occurrence_a, occurrence_b], ClassroomAction.READ)
