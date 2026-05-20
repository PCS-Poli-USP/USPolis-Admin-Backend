from pydantic import field_validator

from server.models.http.requests.permission_request_models import (
    PermissionRegister,
    PermissionUpdate,
)
from server.utils.enums.actions_enums import CourseAction


class CoursePermissionRegister(PermissionRegister):
    course_id: int | None

    @field_validator("actions", mode="before")
    @classmethod
    def validate_actions(
        cls, value: str | CourseAction | list[str | CourseAction]
    ) -> list[CourseAction]:
        if isinstance(value, str | CourseAction):
            value = [value]
        actions: list[CourseAction] = []
        try:
            for action in value:
                actions.append(CourseAction(action))
        except ValueError as exc:
            raise ValueError("actions must be a list of CourseAction") from exc
        return actions


class CoursePermissionUpdate(PermissionUpdate):
    course_id: int | None

    @field_validator("actions", mode="before")
    @classmethod
    def validate_actions(
        cls, value: str | CourseAction | list[str | CourseAction]
    ) -> list[CourseAction]:
        if isinstance(value, str | CourseAction):
            value = [value]
        actions: list[CourseAction] = []
        try:
            for action in value:
                actions.append(CourseAction(action))
        except ValueError as exc:
            raise ValueError("actions must be a list of CourseAction") from exc
        return actions
