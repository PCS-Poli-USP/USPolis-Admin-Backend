from datetime import datetime
from typing import cast

from pydantic import BaseModel

from server.models.database.building_permission_db_model import BuildingPermission
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.course_permission_db_model import CoursePermission
from server.utils.enums.actions_enums import PermissionAction
from server.utils.enums.resources_enums import Resource
from server.utils.permissions_types import Permission, PermissionList
from server.utils.type_guard import TypeGuard


class PermissionResponse(BaseModel):
    id: int
    resource: Resource
    actions: list[PermissionAction]
    resource_id: int
    resource_name: str

    parent_id: int | None = None
    parent_name: str | None = None
    parent_resource: Resource | None = None

    user_id: int | None
    user_name: str | None
    user_email: str | None

    role_id: int | None
    role_name: str | None

    granted_by_id: int
    granted_by: str
    granted_at: datetime

    @classmethod
    def from_permission(
        cls, permission: Permission, resource: Resource
    ) -> "PermissionResponse":
        if resource == Resource.CLASSROOM:
            return cls.from_classroom_permission(permission)  # type: ignore
        if resource == Resource.COURSE:
            return cls.from_course_permission(permission)  # type: ignore
        if resource == Resource.BUILDING:
            return cls.from_building_permission(permission)  # type: ignore
        raise ValueError("Invalid permission type")

    @classmethod
    def from_permissions(
        cls, permissions: PermissionList, resource: Resource
    ) -> list["PermissionResponse"]:
        if resource == Resource.CLASSROOM:
            return cls.from_classroom_permissions(permissions)  # type: ignore

        if resource == Resource.COURSE:
            return cls.from_course_permissions(
                permissions  # type: ignore
            )

        if resource == Resource.BUILDING:
            return cls.from_building_permissions(permissions)  # type: ignore
        
        raise ValueError("Invalid permission type")

    @classmethod
    def from_classroom_permission(
        cls, classroom_permission: ClassroomPermission
    ) -> "PermissionResponse":
        return cls(
            id=TypeGuard.must_be_int(classroom_permission.id),
            resource=Resource.CLASSROOM,
            actions=cast(list, classroom_permission.actions),
            resource_id=classroom_permission.classroom_id or -1,
            resource_name=classroom_permission.classroom.name
            if classroom_permission.classroom
            else "Todas as salas",
            parent_id=classroom_permission.classroom.building_id
            if classroom_permission.classroom
            else None,
            parent_name=classroom_permission.classroom.building.name
            if classroom_permission.classroom
            and classroom_permission.classroom.building
            else "Todos os prédios",
            parent_resource=Resource.BUILDING,
            user_id=classroom_permission.user_id,
            user_name=classroom_permission.user.name
            if classroom_permission.user
            else None,
            user_email=classroom_permission.user.email
            if classroom_permission.user
            else None,
            role_id=classroom_permission.role_id,
            role_name=classroom_permission.role.name
            if classroom_permission.role
            else None,
            granted_by_id=TypeGuard.must_be_int(classroom_permission.granted_by_id),
            granted_by=classroom_permission.granted_by.name,
            granted_at=classroom_permission.granted_at,
        )

    @classmethod
    def from_classroom_permissions(
        cls, classroom_permissions: list[ClassroomPermission]
    ) -> list["PermissionResponse"]:
        return [cls.from_classroom_permission(cp) for cp in classroom_permissions]

    @classmethod
    def from_course_permission(
        cls, course_permission: CoursePermission
    ) -> "PermissionResponse":
        return cls(
            id=TypeGuard.must_be_int(course_permission.id),
            resource=Resource.COURSE,
            actions=cast(list, course_permission.actions),
            resource_id=course_permission.course_id or -1,
            resource_name=course_permission.course.name
            if course_permission.course
            else "Todos os cursos",
            user_id=course_permission.user_id,
            user_name=course_permission.user.name if course_permission.user else None,
            user_email=course_permission.user.email if course_permission.user else None,
            role_id=course_permission.role_id,
            role_name=course_permission.role.name if course_permission.role else None,
            granted_by_id=TypeGuard.must_be_int(course_permission.granted_by_id),
            granted_by=course_permission.granted_by.name,
            granted_at=course_permission.granted_at,
        )

    @classmethod
    def from_course_permissions(
        cls, course_permissions: list[CoursePermission]
    ) -> list["PermissionResponse"]:
        return [cls.from_course_permission(cp) for cp in course_permissions]

    @classmethod
    def from_building_permission(
        cls, building_permission: BuildingPermission
    ) -> "PermissionResponse":
        return cls(
            id=TypeGuard.must_be_int(building_permission.id),
            resource=Resource.BUILDING,
            actions=cast(list, building_permission.actions),
            resource_id=building_permission.building_id or -1,
            resource_name=building_permission.building.name
            if building_permission.building
            else "Todos os prédios",
            user_id=building_permission.user_id,
            user_name=building_permission.user.name
            if building_permission.user
            else None,
            user_email=building_permission.user.email
            if building_permission.user
            else None,
            role_id=building_permission.role_id,
            role_name=building_permission.role.name
            if building_permission.role
            else None,
            granted_by_id=TypeGuard.must_be_int(building_permission.granted_by_id),
            granted_by=building_permission.granted_by.name,
            granted_at=building_permission.granted_at,
        )

    @classmethod
    def from_building_permissions(
        cls, building_permissions: list[BuildingPermission]
    ) -> list["PermissionResponse"]:
        return [cls.from_building_permission(bp) for bp in building_permissions]
