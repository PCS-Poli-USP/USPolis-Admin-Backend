from pydantic import field_validator

from server.models.http.requests.permission_request_models import (
    PermissionRegister,
    PermissionUpdate,
)
from server.utils.enums.actions_enums import CourseAction


class CoursePermissionRegister(PermissionRegister):
    course_id: int | None

    @field_validator("action", mode="before")
    @classmethod
    def validate_action(cls, value: str | CourseAction) -> CourseAction:
        if isinstance(value, CourseAction):
            return value
        try:
            return CourseAction(value)
        except ValueError as exc:
            raise ValueError("action must be a CourseAction") from exc


class CoursePermissionUpdate(PermissionUpdate):
    course_id: int | None

    @field_validator("action", mode="before")
    @classmethod
    def validate_action(cls, value: str | CourseAction) -> CourseAction:
        if isinstance(value, CourseAction):
            return value
        try:
            return CourseAction(value)
        except ValueError as exc:
            raise ValueError("action must be a CourseAction") from exc
