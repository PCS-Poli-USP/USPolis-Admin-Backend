from pydantic import BaseModel

from server.models.database.classroom_db_model import Classroom
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.user_db_model import User
from server.utils.enums.classroom_permission_type_enum import ClassroomPermissionType
from server.utils.must_be_int import must_be_int


class ClassroomPermissionResponse(BaseModel):
    id: int
    classroom_id: int
    classroom_name: str

    permissions: list[ClassroomPermissionType]
    given_by_id: int
    given_by: str

    @classmethod
    def from_permission(
        cls, permission: ClassroomPermission
    ) -> "ClassroomPermissionResponse":
        return cls(
            id=must_be_int(permission.id),
            classroom_id=permission.classroom_id,
            classroom_name=permission.classroom.name,
            permissions=permission.permissions,
            given_by_id=permission.given_by_id,
            given_by=permission.given_by.name,
        )

    @classmethod
    def from_permissions(
        cls, permissions: list[ClassroomPermission]
    ) -> list["ClassroomPermissionResponse"]:
        return [cls.from_permission(permission) for permission in permissions]


class ClassroomPermissionsCore(BaseModel):
    permission_id: int
    permissions: list[ClassroomPermissionType]

    given_by_id: int
    given_by: str
    given_by_email: str


class ClassroomUsersPermissioned(ClassroomPermissionsCore):
    user_id: int
    user_name: str
    user_email: str


class UserClassroomPermissions(ClassroomPermissionsCore):
    classroom_id: int
    classroom_name: str

    building_id: int
    building_name: str


class ClassroomPermissionByUserResponse(BaseModel):
    user_id: int
    user_name: str
    user_email: str

    classroom_permissions: list[UserClassroomPermissions]

    @classmethod
    def from_user(
        cls, user: User, allowed_classrooms_ids: set[int]
    ) -> "ClassroomPermissionByUserResponse":
        """
        Query improvements:
        - Load users with permissions
        - Load permissions with classroom
        - Load classroom with building
        """
        permissions = user.classroom_permissions
        classroom_permission_map: dict[int, UserClassroomPermissions] = {}
        for permission in permissions:
            classroom = permission.classroom
            classroom_id = must_be_int(classroom.id)
            if classroom_id not in allowed_classrooms_ids:
                continue
            building = classroom.building
            if classroom_id not in classroom_permission_map:
                classroom_permission_map[classroom_id] = UserClassroomPermissions(
                    classroom_id=classroom_id,
                    classroom_name=classroom.name,
                    building_id=must_be_int(building.id),
                    building_name=building.name,
                    permission_id=must_be_int(permission.id),
                    permissions=[],
                    given_by_id=permission.given_by_id,
                    given_by=permission.given_by.name,
                    given_by_email=permission.given_by.email,
                )
            classroom_permission_map[classroom_id].permissions = permission.permissions

        classroom_permissions = list(classroom_permission_map.values())
        return cls(
            user_id=must_be_int(user.id),
            user_name=user.name,
            user_email=user.email,
            classroom_permissions=classroom_permissions,
        )

    @classmethod
    def from_users(
        cls, users: list[User], allowed_classrooms_ids: set[int]
    ) -> list["ClassroomPermissionByUserResponse"]:
        """
        Query improvements:
        - Load users with permissions
        - Load permissions with classroom
        - Load classroom with building
        """
        return [cls.from_user(user, allowed_classrooms_ids) for user in users]


class ClassroomPermissionByClassroomResponse(BaseModel):
    classroom_id: int
    classroom_name: str

    building_id: int
    building_name: str

    users_permissioned: list[ClassroomUsersPermissioned]

    @classmethod
    def from_classroom(
        cls, classroom: Classroom
    ) -> "ClassroomPermissionByClassroomResponse":
        """
        Query loads:
        - Load classroom with building and permissions
        - Load permissions with user and given_by
        """
        permissions = classroom.permissions
        user_permissions_map: dict[int, ClassroomUsersPermissioned] = {}
        for permission in permissions:
            user = permission.user
            user_id = must_be_int(user.id)
            if user_id not in user_permissions_map:
                user_permissions_map[user_id] = ClassroomUsersPermissioned(
                    user_id=user_id,
                    user_name=user.name,
                    user_email=user.email,
                    permission_id=must_be_int(permission.id),
                    permissions=[],
                    given_by_id=permission.given_by_id,
                    given_by=permission.given_by.name,
                    given_by_email=permission.given_by.email,
                )
            user_permissions_map[user_id].permissions = permission.permissions

        users_permissioned = list(user_permissions_map.values())
        return cls(
            classroom_id=must_be_int(classroom.id),
            classroom_name=classroom.name,
            building_id=classroom.building_id,
            building_name=classroom.building.name,
            users_permissioned=users_permissioned,
        )

    @classmethod
    def from_classrooms(
        cls, classrooms: list[Classroom]
    ) -> list["ClassroomPermissionByClassroomResponse"]:
        """
        Query loads:
        - Load classroom with building and permissions
        - Load permissions with user and given_by
        """
        return [cls.from_classroom(classroom) for classroom in classrooms]
