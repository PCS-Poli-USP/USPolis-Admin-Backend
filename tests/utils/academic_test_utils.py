"""Shared, DB-free helpers for building User/Building/Classroom/Subject/
Class/Reservation/Occurrence/Exam/Solicitation object graphs in pure unit
tests (no session, nothing persisted).

These delegate to the real tests/factories/model/*ModelFactory classes via
their session-free `.build()` method wherever that's actually safe (most
factories' get_defaults() never touches the session), so unit and
integration tests share the exact same default-population logic (dicts +
Faker) instead of duplicating field lists. See TESTS.md's "Test data
protocol" section before adding a new make_* helper here or a new
XxxModelFactory.

The one exception is `make_exam`: ExamModelFactory.get_defaults() itself
calls reservation_factory.create_and_refresh() (a real session.add/commit),
so ExamModelFactory(...).build() is NOT actually session-free despite the
name - it's constructed directly here instead, with a comment at the call
site explaining why."""

from datetime import date
from typing import Any

from sqlmodel import Session

from server.models.database.allocation_log_db_model import AllocationLog
from server.models.database.building_db_model import Building
from server.models.database.building_permission_db_model import BuildingPermission
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.course_db_model import Course
from server.models.database.course_permission_db_model import CoursePermission
from server.models.database.curriculum_db_model import Curriculum
from server.models.database.event_db_model import Event
from server.models.database.exam_db_model import Exam
from server.models.database.group_db_model import Group
from server.models.database.intentional_conflict_db_model import IntentionalConflict
from server.models.database.meeting_db_model import Meeting
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.occurrence_label_db_model import OccurrenceLabel
from server.models.database.reservation_db_model import Reservation
from server.models.database.role_db_model import Role
from server.models.database.schedule_db_model import Schedule
from server.models.database.solicitation_db_model import Solicitation
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.utils.enums.action_type_enum import ActionType
from server.utils.enums.actions_enums import PermissionAction
from server.utils.enums.event_type_enum import EventType
from server.utils.enums.resources_enums import Resource
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from tests.factories.base.event_base_factory import EventBaseFactory
from tests.factories.base.exam_base_factory import ExamBaseFactory
from tests.factories.base.meeting_base_factory import MeetingBaseFactory
from tests.factories.model.allocation_log_model_factory import AllocationLogModelFactory
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.building_permission_model_factory import (
    BuildingPermissionModelFactory,
)
from tests.factories.model.class_model_factory import ClassModelFactory
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.classroom_permission_model_factory import (
    ClassroomPermissionModelFactory,
)
from tests.factories.model.course_model_factory import CourseModelFactory
from tests.factories.model.course_permission_model_factory import (
    CoursePermissionModelFactory,
)
from tests.factories.model.curriculum_model_factory import CurriculumModelFactory
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.model.intentional_conflict_model_factory import (
    IntentionalConflictModelFactory,
)
from tests.factories.model.occurrence_model_factory import OccurrenceModelFactory
from tests.factories.model.reservation_model_factory import ReservationModelFactory
from tests.factories.model.role_model_factory import RoleModelFactory
from tests.factories.model.subject_model_factory import SubjectModelFactory
from tests.factories.model.user_model_factory import UserModelFactory

_next_id = iter(range(1, 1_000_000))


def _given(**kwargs: Any) -> dict[str, Any]:
    """Drops keys whose value is None, so an unset caller argument falls
    through to the factory's own Faker-based default instead of overriding
    it with an explicit None."""
    return {key: value for key, value in kwargs.items() if value is not None}


def make_user(*, name: str | None = None) -> User:
    user = UserModelFactory(session=Session()).build(**_given(name=name))
    user.id = next(_next_id)
    return user


def make_building(*, name: str | None = None, creator: User | None = None) -> Building:
    building = BuildingModelFactory(creator or make_user(), Session()).build(
        **_given(name=name)
    )
    building.id = next(_next_id)
    return building


def make_classroom(
    *,
    building: Building,
    name: str | None = None,
    capacity: int = 30,
    remote: bool = False,
) -> Classroom:
    classroom = ClassroomModelFactory(
        session=Session(), creator=building.created_by, building=building
    ).build(capacity=capacity, **_given(name=name))
    classroom.id = next(_next_id)
    # ClassroomBaseFactory.get_base_defaults() doesn't set `remote` at all,
    # so passing it as a .build() override is silently dropped (the
    # override merge only touches keys already present in get_defaults())
    # and the DB model's own default (remote=True) wins instead - set it
    # directly here rather than changing the shared factory's defaults,
    # which other tests may implicitly rely on.
    classroom.remote = remote
    return classroom


def make_subject(*, code: str | None = None, name: str | None = None) -> Subject:
    subject = SubjectModelFactory(building=make_building(), session=Session()).build(
        **_given(code=code, name=name)
    )
    subject.id = next(_next_id)
    return subject


def make_class(*, subject: Subject, code: str | None = None, vacancies: int = 40) -> Class:
    class_ = ClassModelFactory(subject=subject, session=Session()).build(
        schedules=[], vacancies=vacancies, **_given(code=code)
    )
    class_.id = next(_next_id)
    class_.subject_id = must_be_int(subject.id)
    return class_


def make_reservation(
    *,
    schedule: Schedule,
    created_by: User | None = None,
    type_: ReservationType = ReservationType.EVENT,
    title: str | None = None,
    reason: str | None = None,
    solicitation: Solicitation | None = None,
) -> Reservation:
    creator = created_by or make_user()
    # ReservationModelFactory requires a classroom, but never actually reads
    # it in get_defaults() (only create()'s auto-schedule step would, and
    # build() skips that) - a throwaway one is fine here.
    reservation = ReservationModelFactory(
        reservation_type=type_,
        creator=creator,
        classroom=make_classroom(building=make_building()),
        session=Session(),
    ).build(**_given(title=title, reason=reason))
    reservation.id = next(_next_id)
    reservation.created_by = creator
    reservation.schedule = schedule
    reservation.exam = None
    reservation.solicitation = solicitation
    schedule.reservation = reservation
    return reservation


def make_occurrence(
    *,
    schedule: Schedule,
    classroom: Classroom | None = None,
    occurrence_date: date = date(2025, 1, 6),
    label: str | None = None,
) -> Occurrence:
    occurrence = OccurrenceModelFactory(
        schedule=schedule, session=Session(), classroom=classroom
    ).build(
        start_time=schedule.start_time, end_time=schedule.end_time, date=occurrence_date
    )
    occurrence.id = next(_next_id)
    occurrence.occurrence_label = (
        OccurrenceLabel(
            id=next(_next_id), occurrence_id=must_be_int(occurrence.id), label=label
        )
        if label
        else None
    )
    return occurrence


def make_exam(*, reservation: Reservation, subject: Subject, classes: list[Class]) -> Exam:
    """Constructed directly (not via ExamModelFactory.build()) because
    ExamModelFactory.get_defaults() itself calls
    reservation_factory.create_and_refresh() - a real DB write - so it isn't
    actually session-free despite build() normally being safe."""
    base = ExamBaseFactory(must_be_int(subject.id)).get_base_defaults()
    exam = Exam(id=next(_next_id), reservation_id=must_be_int(reservation.id), **base)
    exam.reservation = reservation
    exam.subject = subject
    exam.classes = classes
    reservation.exam = exam
    return exam


def make_solicitation(
    *, building: Building, user: User, capacity: int = 10
) -> Solicitation:
    """Reservation.get_building() only reads `solicitation.building` on this
    fallback path, so this deliberately doesn't take a Reservation - the
    reservation that will eventually point at this solicitation doesn't
    exist yet when a caller needs to build one this way."""
    solicitation = Solicitation(
        id=next(_next_id),
        capacity=capacity,
        building_id=must_be_int(building.id),
        reservation_id=next(_next_id),
        user_id=must_be_int(user.id),
    )
    solicitation.building = building
    solicitation.user = user
    return solicitation


def make_event(
    *,
    reservation: Reservation,
    link: str | None = None,
    type_: EventType = EventType.OTHER,
) -> Event:
    """Constructed directly (not via EventModelFactory.build()) because
    EventModelFactory.get_defaults() itself calls
    reservation_factory.create_and_refresh() - a real DB write - so it isn't
    actually session-free despite build() normally being safe."""
    base = EventBaseFactory().get_base_defaults()
    event = Event(
        id=next(_next_id),
        reservation_id=must_be_int(reservation.id),
        type=type_,
        **{**base, **_given(link=link)},
    )
    event.reservation = reservation
    reservation.event = event
    return event


def make_meeting(*, reservation: Reservation, link: str | None = None) -> Meeting:
    """Constructed directly - see make_event's docstring, same reasoning
    applies to MeetingModelFactory."""
    base = MeetingBaseFactory().get_base_defaults()
    meeting = Meeting(
        id=next(_next_id),
        reservation_id=must_be_int(reservation.id),
        **{**base, **_given(link=link)},
    )
    meeting.reservation = reservation
    reservation.meeting = meeting
    return meeting


def make_allocation_log(
    *, schedule: Schedule, action: ActionType = ActionType.ALLOCATE
) -> AllocationLog:
    log = AllocationLogModelFactory(schedule=schedule, session=Session()).build(
        action=action
    )
    log.id = next(_next_id)
    log.schedule = schedule
    return log


def make_intentional_conflict(
    *, first_occurrence: Occurrence, second_occurrence: Occurrence
) -> IntentionalConflict:
    conflict = IntentionalConflictModelFactory(
        first_occurrence=first_occurrence,
        second_occurrence=second_occurrence,
        session=Session(),
    ).build()
    conflict.id = next(_next_id)
    return conflict


def make_group(*, building: Building, name: str | None = None) -> Group:
    group = GroupModelFactory(building=building, session=Session()).build(
        **_given(name=name)
    )
    group.id = next(_next_id)
    group.building = building
    return group


def make_role(*, resources: list[Resource]) -> Role:
    role = RoleModelFactory(session=Session()).build(resources=resources)
    role.id = next(_next_id)
    return role


def make_classroom_permission(
    *,
    role: Role,
    granted_by: User,
    classroom: Classroom | None = None,
    actions: list[PermissionAction] | None = None,
) -> ClassroomPermission:
    permission = ClassroomPermissionModelFactory(
        role=role, granted_by=granted_by, session=Session()
    ).build(
        classroom_id=classroom.id if classroom else None,
        **_given(actions=actions),
    )
    permission.id = next(_next_id)
    permission.role = role
    permission.granted_by = granted_by
    permission.classroom = classroom
    return permission


def make_course_permission(
    *,
    role: Role,
    granted_by: User,
    course: Course | None = None,
    actions: list[PermissionAction] | None = None,
) -> CoursePermission:
    permission = CoursePermissionModelFactory(
        role=role, granted_by=granted_by, session=Session()
    ).build(
        course_id=course.id if course else None,
        **_given(actions=actions),
    )
    permission.id = next(_next_id)
    permission.role = role
    permission.granted_by = granted_by
    permission.course = course
    return permission


def make_building_permission(
    *,
    role: Role,
    granted_by: User,
    building: Building | None = None,
    actions: list[PermissionAction] | None = None,
) -> BuildingPermission:
    permission = BuildingPermissionModelFactory(
        role=role, granted_by=granted_by, session=Session()
    ).build(
        building_id=building.id if building else None,
        **_given(actions=actions),
    )
    permission.id = next(_next_id)
    permission.role = role
    permission.granted_by = granted_by
    permission.building = building
    return permission


def make_course(*, creator: User, name: str | None = None) -> Course:
    course = CourseModelFactory(creator=creator, session=Session()).build(
        **_given(name=name)
    )
    course.id = next(_next_id)
    return course


def make_curriculum(
    *,
    course: Course,
    creator: User,
    codcur: int | None = None,
    codhab: int | None = None,
    description: str | None = None,
) -> Curriculum:
    curriculum = CurriculumModelFactory(
        course=course, creator=creator, session=Session()
    ).build(**_given(codcur=codcur, codhab=codhab, description=description))
    curriculum.id = next(_next_id)
    curriculum.course_id = must_be_int(course.id)
    return curriculum
