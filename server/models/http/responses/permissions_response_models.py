from datetime import datetime
from typing import cast

from pydantic import BaseModel

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
    resource_id: int | None
    user_id: int | None
    role_id: int | None

    granted_by_id: int
    granted_by: str
    granted_at: datetime

    @classmethod
    def from_permission(
        cls, permission: Permission, resource: Resource
    ) -> "PermissionResponse":
        if resource == Resource.CLASSROOM:
            return cls.from_classroom_permission(permission)  # type: ignore
        elif resource == Resource.COURSE:
            return cls.from_course_permission(permission)  # type: ignore
        raise ValueError("Invalid permission type")

    @classmethod
    def from_permissions(
        cls, permissions: PermissionList, resource: Resource
    ) -> list["PermissionResponse"]:
        if resource == Resource.CLASSROOM:
            return cls.from_classroom_permissions(permissions)  # type: ignore
        elif resource == Resource.COURSE:
            return cls.from_course_permissions(
                permissions  # type: ignore
            )
        return []

    @classmethod
    def from_classroom_permission(
        cls, classroom_permission: ClassroomPermission
    ) -> "PermissionResponse":
        return cls(
            id=TypeGuard.must_be_int(classroom_permission.id),
            resource=Resource.CLASSROOM,
            actions=cast(list, classroom_permission.actions),
            resource_id=classroom_permission.classroom_id,
            user_id=classroom_permission.user_id,
            role_id=classroom_permission.role_id,
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
            resource_id=course_permission.course_id,
            user_id=course_permission.user_id,
            role_id=course_permission.role_id,
            granted_by_id=TypeGuard.must_be_int(course_permission.granted_by_id),
            granted_by=course_permission.granted_by.name,
            granted_at=course_permission.granted_at,
        )

    @classmethod
    def from_course_permissions(
        cls, course_permissions: list[CoursePermission]
    ) -> list["PermissionResponse"]:
        return [cls.from_course_permission(cp) for cp in course_permissions]
