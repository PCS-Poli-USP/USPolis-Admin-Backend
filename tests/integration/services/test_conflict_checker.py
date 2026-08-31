from datetime import date, time, timedelta

from sqlmodel import Session

from server.deps.owned_building_ids import owned_building_ids
from server.deps.repository_adapters.building_repository_adapter import (
    BuildingRepositoryAdapter,
)
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryAdapter,
)
from server.deps.repository_adapters.schedule_repository_adapter import (
    ScheduleRepositoryAdapter,
)
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.services.conflict_checker import ConflictChecker
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import BuildingAction
from server.utils.enums.confict_enum import ConflictType
from server.utils.enums.recurrence import Recurrence
from server.utils.must_be_int import must_be_int
from tests.factories.model.class_model_factory import ClassModelFactory
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.intentional_conflict_model_factory import (
    IntentionalConflictModelFactory,
)
from tests.factories.model.occurrence_model_factory import OccurrenceModelFactory
from tests.factories.model.schedule_model_factory import ScheduleModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper

_FUTURE_DATE = date.today() + timedelta(days=10)


def _checker(*, user: User, session: Session) -> ConflictChecker:
    permission_index = build_permission_index(user)
    owned = owned_building_ids(user=user, session=session)
    classroom_repo = ClassroomRepositoryAdapter(
        owned_building_ids=owned,
        session=session,
        user=user,
        permission_index=permission_index,
    )
    schedule_repo = ScheduleRepositoryAdapter(
        owned_building_ids=owned,
        user=user,
        session=session,
        permission_index=permission_index,
    )
    building_repo = BuildingRepositoryAdapter(
        owned_building_ids=owned,
        session=session,
        user=user,
        permission_index=permission_index,
    )
    return ConflictChecker(
        user=user,
        session=session,
        classroom_repository=classroom_repo,
        schedule_repository=schedule_repo,
        building_repository=building_repo,
    )


def _occurrence_in_classroom(
    *,
    subject: Subject,
    classroom: Classroom,
    session: Session,
    start: time,
    end: time,
) -> Occurrence:
    """A real occurrence allocated to `classroom`, backed by its own class/schedule."""
    class_ = ClassModelFactory(subject=subject, session=session).create_and_refresh(
        schedules=[]
    )
    schedule = ScheduleModelFactory(
        class_=class_, session=session
    ).create_and_refresh()
    return OccurrenceModelFactory(
        schedule=schedule, session=session, classroom=classroom
    ).create_and_refresh(date=_FUTURE_DATE, start_time=start, end_time=end)


class TestSpecificateConflictsForAllowedClassroomsInBuilding:
    def test_returns_empty_when_user_has_no_accessible_classrooms(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.READ],
            granted_by=admin_user,
            session=session,
        )
        checker = _checker(user=common_user, session=session)

        result = checker.specificate_conflicts_for_allowed_classrooms_in_building(
            building_id=must_be_int(building.id),
            type=ConflictType.UNINTENTIONAL,
            start=None,
            end=None,
        )

        assert result.total_conflicts == 0
        assert result.conflicts == []

    def test_reports_unintentional_conflicts_in_the_same_classroom(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        subject: Subject,
        session: Session,
    ) -> None:
        # Classroom.remote defaults to True at the model level (the factory
        # never overrides it), and the method under test skips remote
        # classrooms entirely - so it must be turned off for this classroom's
        # conflicts to be counted at all.
        classroom.remote = False
        session.add(classroom)
        session.commit()
        _occurrence_in_classroom(
            subject=subject,
            classroom=classroom,
            session=session,
            start=time(8, 0),
            end=time(10, 0),
        )
        _occurrence_in_classroom(
            subject=subject,
            classroom=classroom,
            session=session,
            start=time(9, 0),
            end=time(11, 0),
        )
        checker = _checker(user=admin_user, session=session)

        result = checker.specificate_conflicts_for_allowed_classrooms_in_building(
            building_id=must_be_int(building.id),
            type=ConflictType.UNINTENTIONAL,
            start=None,
            end=None,
        )

        assert result.total_conflicts == 2
        assert len(result.conflicts) == 1
        assert result.conflicts[0].id == classroom.id
        # One conflicting group of 2 occurrences appends once per occurrence
        # (each keyed by its own subject/class identifier), so this counts
        # occurrence-appearances-in-conflicts, not distinct conflict groups.
        assert result.conflicts[0].total_classroom_conflicts == 2

    def test_excludes_pairs_marked_as_intentional_from_the_unintentional_report(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        subject: Subject,
        session: Session,
    ) -> None:
        classroom.remote = False
        session.add(classroom)
        session.commit()
        first = _occurrence_in_classroom(
            subject=subject,
            classroom=classroom,
            session=session,
            start=time(8, 0),
            end=time(10, 0),
        )
        second = _occurrence_in_classroom(
            subject=subject,
            classroom=classroom,
            session=session,
            start=time(9, 0),
            end=time(11, 0),
        )
        IntentionalConflictModelFactory(
            first_occurrence=first, second_occurrence=second, session=session
        ).create_and_refresh()
        checker = _checker(user=admin_user, session=session)

        unintentional = checker.specificate_conflicts_for_allowed_classrooms_in_building(
            building_id=must_be_int(building.id),
            type=ConflictType.UNINTENTIONAL,
            start=None,
            end=None,
        )
        intentional = checker.specificate_conflicts_for_allowed_classrooms_in_building(
            building_id=must_be_int(building.id),
            type=ConflictType.INTENTIONAL,
            start=None,
            end=None,
        )

        assert unintentional.total_conflicts == 0
        assert intentional.total_conflicts == 2


class TestClassroomsWithConflictsIndicatorForSchedule:
    def test_flags_a_classroom_with_an_overlapping_occurrence(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        subject: Subject,
        session: Session,
    ) -> None:
        other_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        _occurrence_in_classroom(
            subject=subject,
            classroom=classroom,
            session=session,
            start=time(8, 0),
            end=time(10, 0),
        )

        # The hypothetical (unallocated) schedule being checked - CUSTOM
        # recurrence reads occurrences straight off the schedule itself, so
        # attaching one directly gives full control over date/time.
        candidate_class = ClassModelFactory(
            subject=subject, session=session
        ).create_and_refresh(schedules=[])
        candidate_schedule = ScheduleModelFactory(
            class_=candidate_class, session=session
        ).create_and_refresh(recurrence=Recurrence.CUSTOM, allocated=False)
        OccurrenceModelFactory(
            schedule=candidate_schedule, session=session, classroom=None
        ).create_and_refresh(date=_FUTURE_DATE, start_time=time(9, 0), end_time=time(11, 0))
        session.refresh(candidate_schedule)

        checker = _checker(user=admin_user, session=session)

        results = checker.classrooms_with_conflicts_indicator_for_schedule(
            building_id=must_be_int(building.id),
            schedule_id=must_be_int(candidate_schedule.id),
        )

        by_id = {r.id: r for r in results}
        assert by_id[must_be_int(classroom.id)].conflicts == 1
        assert by_id[must_be_int(other_classroom.id)].conflicts == 0
