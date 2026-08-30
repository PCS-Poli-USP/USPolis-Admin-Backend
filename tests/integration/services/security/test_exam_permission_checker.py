import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.exam_db_model import Exam
from server.models.database.group_db_model import Group
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.services.security.classrooms_permission_checker import (
    ForbiddenClassroomAccess,
)
from server.services.security.exam_permission_checker import ExamPermissionChecker
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import ClassroomAction
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.exam_model_factory import ExamModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _create_exam_with_classroom(
    *, classroom: Classroom, subject: Subject, creator: User, session: Session
) -> Exam:
    exam = ExamModelFactory(
        creator=creator, classroom=classroom, subject=subject, session=session
    ).create_and_refresh()
    exam.reservation.schedule.classroom_id = must_be_int(classroom.id)
    session.add(exam.reservation.schedule)
    session.commit()
    session.refresh(exam)
    return exam


def test_exam_checker_admin_bypasses(
    exam: Exam, admin_user: User, session: Session
) -> None:
    checker = ExamPermissionChecker(
        user=admin_user,
        session=session,
        permission_index=build_permission_index(admin_user),
    )
    checker.check_permission(exam, ClassroomAction.READ)


def test_exam_checker_denies_without_group_or_role(
    classroom: Classroom,
    subject: Subject,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    exam = _create_exam_with_classroom(
        classroom=classroom, subject=subject, creator=admin_user, session=session
    )

    checker = ExamPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission(exam, ClassroomAction.READ)


def test_exam_checker_allows_via_classroom_permission_by_object(
    classroom: Classroom,
    subject: Subject,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    exam = _create_exam_with_classroom(
        classroom=classroom, subject=subject, creator=admin_user, session=session
    )

    # A permission can only be granted to a Role, never directly to a user -
    # the helper grants it to a fresh role (as the admin) and assigns that
    # role to common_user, who then has the permission transitively.
    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ExamPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(exam, ClassroomAction.READ)


def test_exam_checker_allows_via_wildcard_classroom_permission(
    classroom: Classroom,
    subject: Subject,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    exam = _create_exam_with_classroom(
        classroom=classroom, subject=subject, creator=admin_user, session=session
    )

    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=-1,
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ExamPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(exam, ClassroomAction.READ)


def test_exam_checker_allows_via_classroom_permission_by_id(
    classroom: Classroom,
    subject: Subject,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    exam = _create_exam_with_classroom(
        classroom=classroom, subject=subject, creator=admin_user, session=session
    )

    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ExamPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    checker.check_permission(must_be_int(exam.id), ClassroomAction.READ)


def test_exam_checker_list_denies_when_any_exam_disallowed(
    classroom: Classroom,
    building: Building,
    group: Group,
    subject: Subject,
    admin_user: User,
    common_user: User,
    session: Session,
) -> None:
    """Grants access to `classroom` only, so exam_a (held in it) is
    individually allowed while exam_b (a different, ungranted classroom) is
    not - proving the list check evaluates every item rather than
    short-circuiting once it finds one allowed entry."""
    other_classroom = ClassroomModelFactory(
        creator=admin_user, building=building, group=group, session=session
    ).create_and_refresh()
    exam_a = _create_exam_with_classroom(
        classroom=classroom, subject=subject, creator=admin_user, session=session
    )
    exam_b = _create_exam_with_classroom(
        classroom=other_classroom, subject=subject, creator=admin_user, session=session
    )

    RolePermissionTestHelper.grant_classroom_permission(
        user=common_user,
        resource_id=must_be_int(classroom.id),
        actions=[ClassroomAction.READ],
        granted_by=admin_user,
        session=session,
    )

    checker = ExamPermissionChecker(
        user=common_user,
        session=session,
        permission_index=build_permission_index(common_user),
    )
    with pytest.raises(ForbiddenClassroomAccess):
        checker.check_permission([exam_a, exam_b], ClassroomAction.READ)
