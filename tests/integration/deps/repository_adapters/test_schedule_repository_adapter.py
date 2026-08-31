import pytest
from sqlmodel import Session

from server.deps.owned_building_ids import owned_building_ids
from server.deps.repository_adapters.schedule_repository_adapter import (
    InvalidScheduleInput,
    ScheduleRepositoryAdapter,
)
from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.repositories.schedule_repository import ScheduleNotFound
from server.services.security.class_permission_checker import ForbiddenClassAccess
from server.services.security.classrooms_permission_checker import (
    ForbiddenClassroomAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.must_be_int import must_be_int
from tests.factories.request.schedule_request_factory import ScheduleRequestFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _adapter(*, user: User, session: Session) -> ScheduleRepositoryAdapter:
    return ScheduleRepositoryAdapter(
        owned_building_ids=owned_building_ids(user=user, session=session),
        user=user,
        session=session,
        permission_index=build_permission_index(user),
    )


class TestGetById:
    def test_denies_when_outside_owned_buildings(
        self, common_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        schedule_id = must_be_int(class_.schedules[0].id)

        with pytest.raises(ScheduleNotFound):
            adapter.get_by_id(schedule_id)

    def test_allows_on_owned_buildings(
        self, restricted_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=restricted_user, session=session)
        schedule_id = must_be_int(class_.schedules[0].id)

        found = adapter.get_by_id(schedule_id)

        assert found.id == schedule_id


class TestGetAllocationLogs:
    def test_denies_when_outside_owned_buildings(
        self, common_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        schedule_id = must_be_int(class_.schedules[0].id)

        with pytest.raises(ScheduleNotFound):
            adapter.get_allocation_logs(schedule_id)

    def test_allows_on_owned_buildings(
        self, restricted_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=restricted_user, session=session)
        schedule_id = must_be_int(class_.schedules[0].id)

        logs = adapter.get_allocation_logs(schedule_id)

        assert logs == class_.schedules[0].logs


class TestCreateWithClass:
    def test_denies_without_class_update_permission(
        self, common_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        input = ScheduleRequestFactory(class_=class_).create_input()

        with pytest.raises(ForbiddenClassAccess):
            adapter.create_with_class(must_be_int(class_.id), input)

    def test_creates_via_granted_building_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        class_: Class,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.UPDATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        input = ScheduleRequestFactory(class_=class_).create_input()

        created = adapter.create_with_class(must_be_int(class_.id), input)

        assert created.class_id == class_.id

    def test_denies_allocation_without_classroom_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        classroom: Classroom,
        class_: Class,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.UPDATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        input = ScheduleRequestFactory(classroom=classroom, class_=class_).create_input(
            classroom_id=must_be_int(classroom.id)
        )

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.create_with_class(must_be_int(class_.id), input)

    def test_allocates_via_granted_classroom_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        classroom: Classroom,
        class_: Class,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.UPDATE],
            granted_by=admin_user,
            session=session,
        )
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.ALLOCATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        input = ScheduleRequestFactory(classroom=classroom, class_=class_).create_input(
            classroom_id=must_be_int(classroom.id)
        )

        created = adapter.create_with_class(must_be_int(class_.id), input)

        assert created.classroom_id == classroom.id
        assert created.allocated is True


class TestCreateManyWithClass:
    def test_raises_when_any_input_has_no_class_id(
        self, admin_user: User, class_: Class, session: Session
    ) -> None:
        adapter = _adapter(user=admin_user, session=session)
        inputs = [
            ScheduleRequestFactory(class_=class_).create_input(),
            ScheduleRequestFactory(class_=class_).create_input(class_id=None),
        ]

        with pytest.raises(InvalidScheduleInput):
            adapter.create_many_with_class(inputs)

    def test_creates_all_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        class_: Class,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.UPDATE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        inputs = [
            ScheduleRequestFactory(class_=class_).create_input(),
            ScheduleRequestFactory(class_=class_).create_input(),
        ]

        created = adapter.create_many_with_class(inputs)

        assert len(created) == 2
        assert all(schedule.class_id == class_.id for schedule in created)
