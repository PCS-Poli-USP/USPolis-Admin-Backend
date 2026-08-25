from datetime import datetime

from server.models.database.building_permission_db_model import BuildingPermission
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.services.security.role_permission_evaluator import build_permission_index
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.enums.resources_enums import Resource


def make_user(*, is_admin: bool = False, roles: list[Role] | None = None) -> User:
    user = User(
        id=1,
        email="user@usp.br",
        is_admin=is_admin,
        name="User",
        picture_url=None,
        updated_at=datetime.now(),
        last_visited=datetime.now(),
    )
    user.roles = roles or []
    return user


def make_role(
    *,
    resources: list[Resource],
    classroom_permissions: list[ClassroomPermission] | None = None,
    building_permissions: list[BuildingPermission] | None = None,
) -> Role:
    role = Role(
        id=1,
        name="Role",
        description="",
        resources=resources,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    role.classroom_permissions = classroom_permissions or []
    role.building_permissions = building_permissions or []
    role.course_permissions = []
    return role


def test_admin_bypasses_every_check() -> None:
    index = build_permission_index(make_user(is_admin=True))

    assert index.has_permission(
        resource=Resource.CLASSROOM, action=ClassroomAction.DELETE, resource_id=42
    )


def test_exact_resource_id_match_grants_access() -> None:
    permission = ClassroomPermission(
        role_id=1, granted_by_id=1, classroom_id=42, actions=[ClassroomAction.READ]
    )
    role = make_role(resources=[Resource.CLASSROOM], classroom_permissions=[permission])
    index = build_permission_index(make_user(roles=[role]))

    assert index.has_permission(
        resource=Resource.CLASSROOM, action=ClassroomAction.READ, resource_id=42
    )


def test_non_matching_resource_id_denies_access() -> None:
    permission = ClassroomPermission(
        role_id=1, granted_by_id=1, classroom_id=42, actions=[ClassroomAction.READ]
    )
    role = make_role(resources=[Resource.CLASSROOM], classroom_permissions=[permission])
    index = build_permission_index(make_user(roles=[role]))

    assert not index.has_permission(
        resource=Resource.CLASSROOM, action=ClassroomAction.READ, resource_id=99
    )


def test_global_wildcard_grants_read_and_create_for_non_admin() -> None:
    permission = ClassroomPermission(
        role_id=1,
        granted_by_id=1,
        classroom_id=None,
        actions=[ClassroomAction.READ, ClassroomAction.CREATE],
    )
    role = make_role(resources=[Resource.CLASSROOM], classroom_permissions=[permission])
    index = build_permission_index(make_user(roles=[role]))

    assert index.has_permission(
        resource=Resource.CLASSROOM, action=ClassroomAction.READ, resource_id=42
    )
    assert index.has_permission(
        resource=Resource.CLASSROOM, action=ClassroomAction.CREATE, resource_id=42
    )


def test_global_wildcard_denies_update_delete_allocate_reserve_for_non_admin() -> None:
    permission = ClassroomPermission(
        role_id=1,
        granted_by_id=1,
        classroom_id=None,
        actions=[
            ClassroomAction.UPDATE,
            ClassroomAction.DELETE,
            ClassroomAction.ALLOCATE,
            ClassroomAction.RESERVE,
        ],
    )
    role = make_role(resources=[Resource.CLASSROOM], classroom_permissions=[permission])
    index = build_permission_index(make_user(roles=[role]))

    for action in (
        ClassroomAction.UPDATE,
        ClassroomAction.DELETE,
        ClassroomAction.ALLOCATE,
        ClassroomAction.RESERVE,
    ):
        assert not index.has_permission(
            resource=Resource.CLASSROOM, action=action, resource_id=42
        )


def test_global_wildcard_grants_update_delete_allocate_reserve_for_admin() -> None:
    index = build_permission_index(make_user(is_admin=True))

    for action in (
        ClassroomAction.UPDATE,
        ClassroomAction.DELETE,
        ClassroomAction.ALLOCATE,
        ClassroomAction.RESERVE,
    ):
        assert index.has_permission(resource=Resource.CLASSROOM, action=action, resource_id=42)


def test_permission_missing_action_denies_access() -> None:
    permission = ClassroomPermission(
        role_id=1, granted_by_id=1, classroom_id=42, actions=[ClassroomAction.READ]
    )
    role = make_role(resources=[Resource.CLASSROOM], classroom_permissions=[permission])
    index = build_permission_index(make_user(roles=[role]))

    assert not index.has_permission(
        resource=Resource.CLASSROOM, action=ClassroomAction.UPDATE, resource_id=42
    )


def test_classroom_permission_cascades_from_building_permission() -> None:
    permission = BuildingPermission(
        role_id=1, granted_by_id=1, building_id=7, actions=[BuildingAction.ALLOCATE]
    )
    role = make_role(resources=[Resource.BUILDING], building_permissions=[permission])
    index = build_permission_index(make_user(roles=[role]))

    assert index.has_classroom_permission(
        action=ClassroomAction.ALLOCATE, classroom_id=42, building_id=7
    )


def test_classroom_permission_cascade_is_scoped_to_the_right_building() -> None:
    permission = BuildingPermission(
        role_id=1, granted_by_id=1, building_id=7, actions=[BuildingAction.ALLOCATE]
    )
    role = make_role(resources=[Resource.BUILDING], building_permissions=[permission])
    index = build_permission_index(make_user(roles=[role]))

    assert not index.has_classroom_permission(
        action=ClassroomAction.ALLOCATE, classroom_id=42, building_id=8
    )


def test_classroom_permission_without_building_id_does_not_cascade() -> None:
    permission = BuildingPermission(
        role_id=1, granted_by_id=1, building_id=7, actions=[BuildingAction.READ]
    )
    role = make_role(resources=[Resource.BUILDING], building_permissions=[permission])
    index = build_permission_index(make_user(roles=[role]))

    assert not index.has_classroom_permission(
        action=ClassroomAction.READ, classroom_id=42, building_id=None
    )


def test_building_action_includes_allocate_and_reserve() -> None:
    assert BuildingAction.ALLOCATE.value == ClassroomAction.ALLOCATE.value
    assert BuildingAction.RESERVE.value == ClassroomAction.RESERVE.value
