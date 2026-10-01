import pytest
from sqlmodel import Session

from server.deps.owned_building_ids import owned_building_ids
from server.deps.repository_adapters.building_repository_adapter import (
    BuildingRepositoryAdapter,
)
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryAdapter,
)
from server.deps.repository_adapters.occurrence_repository_adapter import (
    OccurrenceRepositoryAdapter,
)
from server.deps.repository_adapters.schedule_repository_adapter import (
    ScheduleRepositoryAdapter,
)
from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.http.requests.allocate_request_models import AllocateSchedule
from server.repositories.schedule_repository import ScheduleNotFound
from server.services.conflict_checker import ConflictChecker
from server.services.security.classrooms_permission_checker import (
    ForbiddenClassroomAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import ClassroomAction
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _adapter(*, user: User, session: Session) -> OccurrenceRepositoryAdapter:
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
    conflict_checker = ConflictChecker(
        user=user,
        session=session,
        classroom_repository=classroom_repo,
        schedule_repository=schedule_repo,
        building_repository=building_repo,
    )
    return OccurrenceRepositoryAdapter(
        owned_building_ids=owned,
        session=session,
        user=user,
        classroom_repo=classroom_repo,
        schedule_repo=schedule_repo,
        conflict_checker=conflict_checker,
        permission_index=permission_index,
    )


class TestGetAll:
    def test_admin_sees_every_occurrence(
        self,
        admin_user: User,
        allocated_classroom: Classroom,
        class_: Class,
        session: Session,
    ) -> None:
        adapter = _adapter(user=admin_user, session=session)
        occurrence = class_.schedules[0].occurrences[0]

        occurrences = adapter.get_all()

        assert occurrence.id in [o.id for o in occurrences]

    def test_restricted_user_sees_occurrences_of_owned_buildings(
        self,
        restricted_user: User,
        allocated_classroom: Classroom,
        class_: Class,
        session: Session,
    ) -> None:
        adapter = _adapter(user=restricted_user, session=session)
        occurrence = class_.schedules[0].occurrences[0]

        occurrences = adapter.get_all()

        assert occurrence.id in [o.id for o in occurrences]

    def test_common_user_sees_none(
        self,
        common_user: User,
        allocated_classroom: Classroom,
        class_: Class,
        session: Session,
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        occurrence = class_.schedules[0].occurrences[0]

        assert occurrence.id not in [o.id for o in adapter.get_all()]


class TestGetById:
    def test_denies_without_permission(
        self,
        common_user: User,
        allocated_classroom: Classroom,
        class_: Class,
        session: Session,
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        occurrence = class_.schedules[0].occurrences[0]

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.get_by_id(must_be_int(occurrence.id))

    def test_allows_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        allocated_classroom: Classroom,
        class_: Class,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(allocated_classroom.id),
            actions=[ClassroomAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        occurrence = class_.schedules[0].occurrences[0]

        found = adapter.get_by_id(must_be_int(occurrence.id))

        assert found.id == occurrence.id


class TestAllocateSchedule:
    def test_denies_when_schedule_outside_owned_buildings(
        self, common_user: User, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ScheduleNotFound):
            adapter.allocate_schedule(
                must_be_int(class_.schedules[0].id), must_be_int(classroom.id)
            )

    def test_denies_without_classroom_allocate_permission(
        self,
        admin_user: User,
        restricted_user: User,
        building: Building,
        class_: Class,
        session: Session,
    ) -> None:
        # restricted_user owns `building` (so the schedule, tied to it, is
        # reachable) but target_classroom has no group and no permission
        # grant of its own - this isolates the classroom-side ALLOCATE check
        # from the building-ownership check.
        target_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        RolePermissionTestHelper.grant_classroom_permission(
            user=restricted_user,
            resource_id=must_be_int(target_classroom.id),
            actions=[ClassroomAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=restricted_user, session=session)

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.allocate_schedule(
                must_be_int(class_.schedules[0].id), must_be_int(target_classroom.id)
            )

    def test_allocates_via_granted_permissions(
        self,
        admin_user: User,
        restricted_user: User,
        building: Building,
        class_: Class,
        session: Session,
    ) -> None:
        target_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        RolePermissionTestHelper.grant_classroom_permission(
            user=restricted_user,
            resource_id=must_be_int(target_classroom.id),
            actions=[ClassroomAction.READ, ClassroomAction.ALLOCATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=restricted_user, session=session)

        updated = adapter.allocate_schedule(
            must_be_int(class_.schedules[0].id), must_be_int(target_classroom.id)
        )

        assert updated.classroom_id == target_classroom.id
        assert updated.allocated is True


class TestAllocateScheduleMany:
    def test_denies_when_schedule_outside_owned_buildings(
        self, common_user: User, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        pairs = [
            AllocateSchedule(
                schedule_id=must_be_int(class_.schedules[0].id),
                classroom_id=must_be_int(classroom.id),
            )
        ]

        with pytest.raises(ScheduleNotFound):
            adapter.allocate_schedule_many(pairs)

    def test_denies_without_classroom_allocate_permission(
        self,
        admin_user: User,
        restricted_user: User,
        building: Building,
        class_: Class,
        session: Session,
    ) -> None:
        target_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        RolePermissionTestHelper.grant_classroom_permission(
            user=restricted_user,
            resource_id=must_be_int(target_classroom.id),
            actions=[ClassroomAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=restricted_user, session=session)
        pairs = [
            AllocateSchedule(
                schedule_id=must_be_int(class_.schedules[0].id),
                classroom_id=must_be_int(target_classroom.id),
            )
        ]

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.allocate_schedule_many(pairs)

    def test_allocates_all_via_granted_permissions(
        self,
        admin_user: User,
        restricted_user: User,
        building: Building,
        class_: Class,
        session: Session,
    ) -> None:
        target_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        RolePermissionTestHelper.grant_classroom_permission(
            user=restricted_user,
            resource_id=must_be_int(target_classroom.id),
            actions=[ClassroomAction.READ, ClassroomAction.ALLOCATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=restricted_user, session=session)
        pairs = [
            AllocateSchedule(
                schedule_id=must_be_int(class_.schedules[0].id),
                classroom_id=must_be_int(target_classroom.id),
            )
        ]

        adapter.allocate_schedule_many(pairs)
        session.refresh(class_.schedules[0])

        assert class_.schedules[0].classroom_id == target_classroom.id


class TestRemoveScheduleAllocation:
    def test_removes_the_allocation(
        self,
        admin_user: User,
        allocated_classroom: Classroom,
        class_: Class,
        session: Session,
    ) -> None:
        adapter = _adapter(user=admin_user, session=session)
        schedule_id = must_be_int(class_.schedules[0].id)

        updated = adapter.remove_schedule_allocation(schedule_id)

        assert updated.classroom_id is None
        assert updated.allocated is False
