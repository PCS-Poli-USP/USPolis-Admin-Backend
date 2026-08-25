from pydantic import field_validator

from server.models.http.requests.permission_request_models import (
    PermissionRegister,
    PermissionUpdate,
)
from server.utils.enums.actions_enums import ClassroomAction


class ClassroomPermissionRegister(PermissionRegister):
    classroom_id: int | None

    @field_validator("actions", mode="before")
    @classmethod
    def validate_actions(
        cls, value: str | ClassroomAction | list[str | ClassroomAction]
    ) -> list[ClassroomAction]:
        if isinstance(value, str | ClassroomAction):
            value = [value]
        actions: list[ClassroomAction] = []
        try:
            for action in value:
                actions.append(ClassroomAction(action))
        except ValueError as exc:
            raise ValueError("actions must be a list of ClassroomAction") from exc
        return actions


class ClassroomPermissionUpdate(PermissionUpdate):
    classroom_id: int | None

    @field_validator("actions", mode="before")
    @classmethod
    def validate_actions(
        cls, value: str | ClassroomAction | list[str | ClassroomAction]
    ) -> list[ClassroomAction]:
        if isinstance(value, str | ClassroomAction):
            value = [value]
        actions: list[ClassroomAction] = []
        try:
            for action in value:
                actions.append(ClassroomAction(action))
        except ValueError as exc:
            raise ValueError("actions must be a list of ClassroomAction") from exc
        return actions
