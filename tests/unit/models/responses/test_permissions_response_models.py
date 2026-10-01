import pytest

from server.models.http.responses.permissions_response_models import PermissionResponse
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction, CourseAction
from server.utils.enums.resources_enums import Resource
from tests.utils.academic_test_utils import (
    make_building,
    make_building_permission,
    make_classroom,
    make_classroom_permission,
    make_course,
    make_course_permission,
    make_role,
    make_user,
)


class TestPermissionResponseFromClassroomPermission:
    def test_with_a_specific_classroom(self) -> None:
        role = make_role(resources=[Resource.CLASSROOM])
        granter = make_user()
        building = make_building(name="Bloco A")
        classroom = make_classroom(building=building, name="Sala 1")
        permission = make_classroom_permission(
            role=role,
            granted_by=granter,
            classroom=classroom,
            actions=[ClassroomAction.READ],
        )

        data = PermissionResponse.from_classroom_permission(permission)

        assert data.resource == Resource.CLASSROOM
        assert data.actions == [ClassroomAction.READ]
        assert data.resource_id == classroom.id
        assert data.resource_name == "Sala 1"
        assert data.parent_id == building.id
        assert data.parent_name == "Bloco A"
        assert data.role_id == role.id
        assert data.role_name == role.name
        assert data.granted_by_id == granter.id
        assert data.granted_by == granter.name

    def test_without_a_classroom_grants_every_classroom(self) -> None:
        role = make_role(resources=[Resource.CLASSROOM])
        granter = make_user()
        permission = make_classroom_permission(role=role, granted_by=granter, classroom=None)

        data = PermissionResponse.from_classroom_permission(permission)

        assert data.resource_id == -1
        assert data.resource_name == "Todas as salas"
        assert data.parent_id is None
        assert data.parent_name == "Todos os prédios"

    def test_from_classroom_permissions(self) -> None:
        role = make_role(resources=[Resource.CLASSROOM])
        granter = make_user()
        p1 = make_classroom_permission(role=role, granted_by=granter)
        p2 = make_classroom_permission(role=role, granted_by=granter)

        data = PermissionResponse.from_classroom_permissions([p1, p2])

        assert [d.id for d in data] == [p1.id, p2.id]


class TestPermissionResponseFromCoursePermission:
    def test_with_a_specific_course(self) -> None:
        role = make_role(resources=[Resource.COURSE])
        granter = make_user()
        course = make_course(creator=granter, name="Ciência da Computação")
        permission = make_course_permission(
            role=role, granted_by=granter, course=course, actions=[CourseAction.READ]
        )

        data = PermissionResponse.from_course_permission(permission)

        assert data.resource == Resource.COURSE
        assert data.resource_id == course.id
        assert data.resource_name == "Ciência da Computação"
        assert data.role_id == role.id

    def test_without_a_course_grants_every_course(self) -> None:
        role = make_role(resources=[Resource.COURSE])
        granter = make_user()
        permission = make_course_permission(role=role, granted_by=granter, course=None)

        data = PermissionResponse.from_course_permission(permission)

        assert data.resource_id == -1
        assert data.resource_name == "Todos os cursos"


class TestPermissionResponseFromBuildingPermission:
    def test_with_a_specific_building(self) -> None:
        role = make_role(resources=[Resource.BUILDING])
        granter = make_user()
        building = make_building(name="Bloco A")
        permission = make_building_permission(
            role=role,
            granted_by=granter,
            building=building,
            actions=[BuildingAction.READ],
        )

        data = PermissionResponse.from_building_permission(permission)

        assert data.resource == Resource.BUILDING
        assert data.resource_id == building.id
        assert data.resource_name == "Bloco A"

    def test_without_a_building_grants_every_building(self) -> None:
        role = make_role(resources=[Resource.BUILDING])
        granter = make_user()
        permission = make_building_permission(role=role, granted_by=granter, building=None)

        data = PermissionResponse.from_building_permission(permission)

        assert data.resource_id == -1
        assert data.resource_name == "Todos os prédios"


class TestPermissionResponseFromPermissionDispatch:
    def test_dispatches_by_resource(self) -> None:
        role = make_role(resources=[Resource.CLASSROOM])
        granter = make_user()
        permission = make_classroom_permission(role=role, granted_by=granter)

        data = PermissionResponse.from_permission(permission, Resource.CLASSROOM)

        assert data.id == permission.id

    def test_dispatches_course_resource(self) -> None:
        role = make_role(resources=[Resource.COURSE])
        granter = make_user()
        course = make_course(creator=granter)
        permission = make_course_permission(role=role, granted_by=granter, course=course)

        data = PermissionResponse.from_permission(permission, Resource.COURSE)

        assert data.id == permission.id
        assert data.resource == Resource.COURSE

    def test_dispatches_building_resource(self) -> None:
        role = make_role(resources=[Resource.BUILDING])
        granter = make_user()
        building = make_building()
        permission = make_building_permission(
            role=role, granted_by=granter, building=building
        )

        data = PermissionResponse.from_permission(permission, Resource.BUILDING)

        assert data.id == permission.id
        assert data.resource == Resource.BUILDING

    def test_raises_for_an_unsupported_resource(self) -> None:
        role = make_role(resources=[Resource.CLASSROOM])
        granter = make_user()
        permission = make_classroom_permission(role=role, granted_by=granter)

        with pytest.raises(ValueError, match="Invalid permission type"):
            PermissionResponse.from_permission(permission, "unsupported")  # type: ignore[arg-type]

    def test_from_permissions_dispatches_by_resource(self) -> None:
        role = make_role(resources=[Resource.CLASSROOM])
        granter = make_user()
        permission = make_classroom_permission(role=role, granted_by=granter)

        data = PermissionResponse.from_permissions([permission], Resource.CLASSROOM)

        assert [d.id for d in data] == [permission.id]

    def test_from_permissions_raises_for_an_unsupported_resource(self) -> None:
        with pytest.raises(ValueError, match="Invalid permission type"):
            PermissionResponse.from_permissions([], "unsupported")  # type: ignore[arg-type]
