from pydantic import field_validator

from server.models.http.requests.permission_request_models import (
    PermissionRegister,
    PermissionUpdate,
)
from server.utils.enums.actions_enums import ClassroomAction


class ClassroomPermissionRegister(PermissionRegister):
    classroom_id: int | None

    @field_validator("action", mode="before")
    @classmethod
    def validate_action(cls, value: str | ClassroomAction) -> ClassroomAction:
        if isinstance(value, ClassroomAction):
            return value
        try:
            return ClassroomAction(value)
        except ValueError as exc:
            raise ValueError("action must be a ClassroomAction") from exc


class ClassroomPermissionUpdate(PermissionUpdate):
    classroom_id: int | None

    @field_validator("action", mode="before")
    @classmethod
    def validate_action(cls, value: str | ClassroomAction) -> ClassroomAction:
        if isinstance(value, ClassroomAction):
            return value
        try:
            return ClassroomAction(value)
        except ValueError as exc:
            raise ValueError("action must be a ClassroomAction") from exc
