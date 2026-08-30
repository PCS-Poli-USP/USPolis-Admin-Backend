from server.models.http.responses.user_response_models import (
    UseCoreResponse,
    UserGroupResponse,
    UserPermissionResponse,
    UserResponse,
)
from server.utils.enums.actions_enums import ClassroomAction
from server.utils.enums.resources_enums import Resource
from tests.utils.academic_test_utils import (
    make_building,
    make_classroom,
    make_classroom_permission,
    make_course,
    make_curriculum,
    make_group,
    make_role,
    make_user,
)


class TestUserGroupResponse:
    def test_from_group_that_is_not_main_uses_its_own_classrooms(self) -> None:
        building = make_building(name="Bloco A")
        group = make_group(building=building, name="Monitores")
        classroom = make_classroom(building=building, name="Sala 1")
        group.classrooms = [classroom]

        data = UserGroupResponse.from_group(group)

        assert data.main is False
        assert data.building == "Bloco A"
        assert data.classroom_ids == [classroom.id]
        assert data.classroom_strs == ["Sala 1 (Bloco A)"]

    def test_from_main_group_uses_all_of_the_buildings_classrooms(self) -> None:
        building = make_building(name="Bloco B")
        group = make_group(building=building, name="Todos")
        building.main_group_id = group.id
        classroom1 = make_classroom(building=building, name="Sala 2")
        classroom2 = make_classroom(building=building, name="Sala 1")
        building.classrooms = [classroom1, classroom2]
        group.classrooms = []

        data = UserGroupResponse.from_group(group)

        assert data.main is True
        assert [c for c in data.classroom_strs] == [
            "Sala 1 (Bloco B)",
            "Sala 2 (Bloco B)",
        ]

    def test_from_group_list(self) -> None:
        building = make_building()
        group1 = make_group(building=building)
        group1.classrooms = []
        group2 = make_group(building=building)
        group2.classrooms = []

        data = UserGroupResponse.from_group_list([group1, group2])

        assert [d.id for d in data] == [group1.id, group2.id]


class TestUserPermissionResponse:
    def test_from_user_collects_permissions_across_roles(self) -> None:
        user = make_user()
        role = make_role(resources=[Resource.CLASSROOM])
        permission = make_classroom_permission(
            role=role, granted_by=user, actions=[ClassroomAction.READ]
        )
        role.classroom_permissions = [permission]
        role.course_permissions = []
        role.building_permissions = []
        user.roles = [role]

        data = UserPermissionResponse.from_user(user)

        assert data.id == user.id
        assert data.resources == [Resource.CLASSROOM]
        assert [p.id for p in data.permissions] == [permission.id]
        assert [r.id for r in data.roles] == [role.id]

    def test_from_user_without_roles_has_no_permissions(self) -> None:
        user = make_user()
        user.roles = []

        data = UserPermissionResponse.from_user(user)

        assert data.resources == []
        assert data.permissions == []
        assert data.roles == []

    def test_from_user_list(self) -> None:
        user1 = make_user()
        user1.roles = []
        user2 = make_user()
        user2.roles = []

        data = UserPermissionResponse.from_user_list([user1, user2])

        assert [d.id for d in data] == [user1.id, user2.id]


class TestUseCoreResponse:
    def test_core_from_user_without_buildings_or_groups(self) -> None:
        user = make_user()
        user.buildings = []
        user.groups = []
        user.created_by = None

        data = UseCoreResponse.core_from_user(user)

        assert data.id == user.id
        assert data.building_ids == []
        assert data.building_names == []
        assert data.group_ids == []
        assert data.group_names == []
        assert data.created_by is None

    def test_core_from_user_with_buildings_groups_and_creator(self) -> None:
        creator = make_user()
        user = make_user()
        user.created_by = creator
        building = make_building(name="Bloco A")
        user.buildings = [building]
        group = make_group(building=building, name="Monitores")
        user.groups = [group]

        data = UseCoreResponse.core_from_user(user)

        assert data.created_by == creator.name
        assert data.building_ids == [building.id]
        assert data.building_names == ["Bloco A"]
        assert data.group_ids == [group.id]
        assert data.group_names == ["Monitores"]

    def test_core_from_user_list(self) -> None:
        user1 = make_user()
        user1.buildings = []
        user1.groups = []
        user1.created_by = None
        user2 = make_user()
        user2.buildings = []
        user2.groups = []
        user2.created_by = None

        data = UseCoreResponse.core_from_user_list([user1, user2])

        assert [d.id for d in data] == [user1.id, user2.id]


class TestUserResponse:
    def test_from_user_minimal(self) -> None:
        user = make_user()
        user.buildings = []
        user.groups = []
        user.solicitations = []
        user.created_by = None
        user.curriculum = None
        user.current_schedule_id = None

        data = UserResponse.from_user(user)

        assert data.id == user.id
        assert data.buildings is None
        assert data.solicitations == []
        assert data.groups == []
        assert data.curriculum is None
        assert data.current_schedule_id is None

    def test_from_user_with_buildings_and_curriculum(self) -> None:
        user = make_user()
        building = make_building(name="Bloco A")
        user.buildings = [building]
        user.groups = []
        user.solicitations = []
        user.created_by = None
        user.current_schedule_id = None

        course = make_course(creator=user, name="Ciência da Computação")
        curriculum = make_curriculum(course=course, creator=user)
        user.curriculum = curriculum

        data = UserResponse.from_user(user)

        assert data.buildings is not None
        assert data.buildings[0].name == "Bloco A"
        assert data.curriculum is not None
        assert data.curriculum.id == curriculum.id

    def test_from_user_list(self) -> None:
        user1 = make_user()
        user1.buildings = []
        user1.groups = []
        user1.solicitations = []
        user1.created_by = None
        user1.curriculum = None
        user1.current_schedule_id = None
        user2 = make_user()
        user2.buildings = []
        user2.groups = []
        user2.solicitations = []
        user2.created_by = None
        user2.curriculum = None
        user2.current_schedule_id = None

        data = UserResponse.from_user_list([user1, user2])

        assert [d.id for d in data] == [user1.id, user2.id]
