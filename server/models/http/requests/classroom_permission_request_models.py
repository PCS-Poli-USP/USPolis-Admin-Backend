from pydantic import BaseModel

from server.utils.enums.classroom_permission_type_enum import ClassroomPermissionType


class ClassroomPermissionRegister(BaseModel):
    """Register a classroom permission for a user."""

    classroom_id: int
    user_id: int
    permissions: list[ClassroomPermissionType]


class ClassroomPermissionManyRegister(BaseModel):
    """Register multiple classroom permissions at once."""

    data: list[ClassroomPermissionRegister]


class ClassroomPermissionUpdate(BaseModel):
    """Update a classroom permission for a user."""

    permissions: list[ClassroomPermissionType]


class ClassroomPermissionManyUpdate(BaseModel):
    """Update multiple classroom permissions at once."""

    inputs: list[ClassroomPermissionUpdate]
