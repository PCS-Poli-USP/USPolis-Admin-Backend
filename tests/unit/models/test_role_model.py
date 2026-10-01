from datetime import datetime

from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.course_permission_db_model import CoursePermission
from server.models.database.role_db_model import Role
from server.utils.enums.actions_enums import ClassroomAction, CourseAction
from server.utils.enums.resources_enums import Resource


def make_role(resources: list[Resource]) -> Role:
    return Role(
        id=1,
        name="Coordenador",
        description="",
        resources=resources,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def test_extend_resource_adds_new_resource() -> None:
    role = make_role([Resource.CLASSROOM])

    role.extend_resource(Resource.COURSE)

    assert role.resources == [Resource.CLASSROOM, Resource.COURSE]


def test_extend_resource_does_not_duplicate() -> None:
    role = make_role([Resource.CLASSROOM])

    role.extend_resource(Resource.CLASSROOM)

    assert role.resources == [Resource.CLASSROOM]


def test_get_permissions_aggregates_every_resource() -> None:
    role = make_role([Resource.CLASSROOM, Resource.COURSE])
    classroom_permission = ClassroomPermission(
        role_id=1, granted_by_id=1, classroom_id=None, actions=[ClassroomAction.READ]
    )
    course_permission = CoursePermission(
        role_id=1, granted_by_id=1, course_id=None, actions=[CourseAction.READ]
    )
    role.classroom_permissions = [classroom_permission]
    role.course_permissions = [course_permission]

    permissions = role.get_permissions()

    assert permissions == [classroom_permission, course_permission]


def test_get_resource_permissions_returns_empty_for_unassigned_resource() -> None:
    role = make_role([Resource.CLASSROOM])
    role.course_permissions = [
        CoursePermission(
            role_id=1, granted_by_id=1, course_id=None, actions=[CourseAction.READ]
        )
    ]

    assert role.get_resource_permissions(Resource.COURSE) == []


def test_get_resource_permissions_map_only_includes_role_resources() -> None:
    role = make_role([Resource.CLASSROOM])
    classroom_permission = ClassroomPermission(
        role_id=1, granted_by_id=1, classroom_id=None, actions=[ClassroomAction.READ]
    )
    role.classroom_permissions = [classroom_permission]
    role.course_permissions = [
        CoursePermission(
            role_id=1, granted_by_id=1, course_id=None, actions=[CourseAction.READ]
        )
    ]

    permissions_map = role.get_resource_permissions_map()

    assert permissions_map == {Resource.CLASSROOM: [classroom_permission]}
