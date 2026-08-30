from server.models.http.responses.role_response_models import RoleResponse
from server.utils.enums.actions_enums import ClassroomAction
from server.utils.enums.resources_enums import Resource
from tests.utils.academic_test_utils import (
    make_classroom_permission,
    make_role,
    make_user,
)


class TestRoleResponse:
    def test_from_role_includes_its_permissions(self) -> None:
        role = make_role(resources=[Resource.CLASSROOM])
        granter = make_user()
        permission = make_classroom_permission(
            role=role, granted_by=granter, actions=[ClassroomAction.READ]
        )
        role.classroom_permissions = [permission]
        role.course_permissions = []
        role.building_permissions = []

        data = RoleResponse.from_role(role)

        assert data.id == role.id
        assert data.name == role.name
        assert data.resources == [Resource.CLASSROOM]
        assert [p.id for p in data.permissions] == [permission.id]

    def test_from_role_without_permissions(self) -> None:
        role = make_role(resources=[])
        role.classroom_permissions = []
        role.course_permissions = []
        role.building_permissions = []

        data = RoleResponse.from_role(role)

        assert data.permissions == []

    def test_from_roles(self) -> None:
        role1 = make_role(resources=[])
        role1.classroom_permissions = []
        role1.course_permissions = []
        role1.building_permissions = []
        role2 = make_role(resources=[])
        role2.classroom_permissions = []
        role2.course_permissions = []
        role2.building_permissions = []

        data = RoleResponse.from_roles([role1, role2])

        assert [d.id for d in data] == [role1.id, role2.id]
