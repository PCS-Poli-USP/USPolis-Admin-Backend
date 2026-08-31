import pytest
from sqlmodel import Session

from server.deps.owned_building_ids import owned_building_ids
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomInsertionOnInvalidGroup,
    ClassroomNameAlreadyExists,
    ClassroomRepositoryAdapter,
    DeleteLastClassroomOnGroups,
)
from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.group_db_model import Group
from server.models.database.user_db_model import User
from server.repositories.occurrence_repository import OccurrenceRepository
from server.services.security.buildings_permission_checker import (
    ForbiddenBuildingAccess,
)
from server.services.security.classrooms_permission_checker import (
    ForbiddenClassroomAccess,
)
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.request.classroom_request_factory import ClassroomRequestFactory
from tests.utils.permission_test_utils import RolePermissionTestHelper


def _adapter(*, user: User, session: Session) -> ClassroomRepositoryAdapter:
    return ClassroomRepositoryAdapter(
        owned_building_ids=owned_building_ids(user=user, session=session),
        session=session,
        user=user,
        permission_index=build_permission_index(user),
    )


class TestGetAll:
    def test_admin_sees_every_classroom(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        adapter = _adapter(user=admin_user, session=session)

        classrooms = adapter.get_all()

        assert classroom.id in [c.id for c in classrooms]

    def test_restricted_user_sees_classrooms_via_main_group(
        self, restricted_user: User, group: Group, classroom: Classroom, session: Session
    ) -> None:
        adapter = _adapter(user=restricted_user, session=session)

        classrooms = adapter.get_all()

        assert [c.id for c in classrooms] == [classroom.id]

    def test_common_user_sees_none(
        self, common_user: User, classroom: Classroom, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        assert adapter.get_all() == []


class TestGetAllOnBuilding:
    def test_denies_without_permission(
        self, common_user: User, building: Building, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenBuildingAccess):
            adapter.get_all_on_building(must_be_int(building.id))

    def test_allows_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)

        classrooms = adapter.get_all_on_building(must_be_int(building.id))

        assert classroom.id in [c.id for c in classrooms]


class TestGetAllOnMyBuildings:
    def test_returns_classrooms_of_owned_buildings(
        self, restricted_user: User, classroom: Classroom, session: Session
    ) -> None:
        adapter = _adapter(user=restricted_user, session=session)

        classrooms = adapter.get_all_on_my_buildings()

        assert [c.id for c in classrooms] == [classroom.id]


class TestGetById:
    def test_denies_without_permission(
        self, common_user: User, classroom: Classroom, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.get_by_id(must_be_int(classroom.id))

    def test_allows_via_granted_permission(
        self, admin_user: User, common_user: User, classroom: Classroom, session: Session
    ) -> None:
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)

        found = adapter.get_by_id(must_be_int(classroom.id))

        assert found.id == classroom.id


class TestGetByIds:
    def test_denies_when_any_classroom_is_disallowed(
        self, common_user: User, classroom: Classroom, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.get_by_ids([must_be_int(classroom.id)])


class TestGetByNameAndBuilding:
    def test_denies_without_permission(
        self, common_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.get_by_name_and_building(classroom.name, building)

    def test_allows_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.READ],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)

        found = adapter.get_by_name_and_building(classroom.name, building)

        assert found.id == classroom.id


class TestCreate:
    def test_denies_without_building_creation_permission(
        self, common_user: User, building: Building, group: Group, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        input = ClassroomRequestFactory(group=group).create_input()

        with pytest.raises(ForbiddenBuildingAccess):
            adapter.create(input)

    def test_creates_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        group: Group,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_building_permission(
            user=common_user,
            resource_id=must_be_int(building.id),
            actions=[BuildingAction.CREATE],
            granted_by=admin_user,
            session=session,
        )
        # A classroom must belong to at least one group, and
        # GroupPermissionChecker (unrelated to the building/classroom
        # permission being tested here) checks actual group membership, not
        # a role grant - so common_user must be a real member of `group`.
        group.users.append(common_user)
        session.add(group)
        session.commit()
        adapter = _adapter(user=common_user, session=session)
        input = ClassroomRequestFactory(group=group).create_input()

        created = adapter.create(input)

        assert created.name == input.name
        assert created.building_id == building.id

    def test_raises_on_duplicate_name_in_the_same_building(
        self, admin_user: User, building: Building, group: Group, classroom: Classroom, session: Session
    ) -> None:
        adapter = _adapter(user=admin_user, session=session)
        input = ClassroomRequestFactory(group=group).create_input(name=classroom.name)

        with pytest.raises(ClassroomNameAlreadyExists):
            adapter.create(input)

    def test_raises_when_a_group_belongs_to_a_different_building(
        self, admin_user: User, building: Building, group: Group, session: Session
    ) -> None:
        other_building = BuildingModelFactory(admin_user, session).create_and_refresh()
        other_group = GroupModelFactory(
            building=other_building, session=session
        ).create_and_refresh(classrooms=[])
        adapter = _adapter(user=admin_user, session=session)
        input = ClassroomRequestFactory(group=group).create_input(
            group_ids=[must_be_int(other_group.id)]
        )

        with pytest.raises(ClassroomInsertionOnInvalidGroup):
            adapter.create(input)


class TestUpdate:
    def test_denies_without_permission(
        self, common_user: User, group: Group, classroom: Classroom, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)
        input = ClassroomRequestFactory(group=group).update_input()

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.update(must_be_int(classroom.id), input)

    def test_updates_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        group: Group,
        classroom: Classroom,
        session: Session,
    ) -> None:
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(classroom.id),
            actions=[ClassroomAction.UPDATE],
            granted_by=admin_user,
            session=session,
        )
        # See the equivalent note in TestCreate - group membership (not the
        # classroom permission under test) gates which groups can be set.
        group.users.append(common_user)
        session.add(group)
        session.commit()
        adapter = _adapter(user=common_user, session=session)
        input = ClassroomRequestFactory(group=group).update_input(name="Nova Sala")

        updated = adapter.update(must_be_int(classroom.id), input)

        assert updated.name == "Nova Sala"


class TestDelete:
    def test_denies_without_permission(
        self, common_user: User, classroom: Classroom, session: Session
    ) -> None:
        adapter = _adapter(user=common_user, session=session)

        with pytest.raises(ForbiddenClassroomAccess):
            adapter.delete(must_be_int(classroom.id))

    def test_raises_when_it_is_the_last_classroom_of_a_group(
        self, admin_user: User, group: Group, classroom: Classroom, session: Session
    ) -> None:
        group.classrooms = [classroom]
        session.add(group)
        session.commit()
        adapter = _adapter(user=admin_user, session=session)

        with pytest.raises(DeleteLastClassroomOnGroups):
            adapter.delete(must_be_int(classroom.id))

    def test_deletes_a_classroom_with_an_allocated_schedule(
        self, admin_user: User, building: Building, class_: Class, session: Session
    ) -> None:
        # A classroom with no group (so the "last classroom of a group"
        # guard above doesn't apply) but with a schedule allocated to it -
        # deleting it must deallocate that schedule first, or the delete
        # fails with an unhandled IntegrityError since Schedule.classroom_id
        # has no ON DELETE CASCADE.
        target_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        OccurrenceRepository.allocate_schedule(
            user=admin_user,
            schedule=class_.schedules[0],
            classroom=target_classroom,
            session=session,
        )
        session.commit()
        adapter = _adapter(user=admin_user, session=session)
        classroom_id = must_be_int(target_classroom.id)

        adapter.delete(classroom_id)
        session.commit()

        assert session.get(Classroom, classroom_id) is None

    def test_deletes_via_granted_permission(
        self,
        admin_user: User,
        common_user: User,
        building: Building,
        session: Session,
    ) -> None:
        other_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        RolePermissionTestHelper.grant_classroom_permission(
            user=common_user,
            resource_id=must_be_int(other_classroom.id),
            actions=[ClassroomAction.DELETE],
            granted_by=admin_user,
            session=session,
        )
        adapter = _adapter(user=common_user, session=session)
        classroom_id = must_be_int(other_classroom.id)

        adapter.delete(classroom_id)
        session.commit()

        assert session.get(Classroom, classroom_id) is None
