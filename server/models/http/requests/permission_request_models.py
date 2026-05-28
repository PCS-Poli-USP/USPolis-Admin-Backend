from typing import Self

from fastapi import HTTPException, status
from pydantic import BaseModel, model_validator

from server.utils.enums.actions_enums import (
    ClassroomAction,
    CourseAction,
    PermissionAction,
)
from server.utils.enums.resources_enums import Resource


class PermissionRegister(BaseModel):
    resource: Resource
    resource_id: int
    actions: list[PermissionAction]
    user_id: int | None = None
    role_id: int | None = None

    @model_validator(mode="after")
    def check_permission_body(self) -> Self:
        if self.user_id is None and self.role_id is None:
            raise PermissionMissingTarget(data_info="User ID ou Role ID")
        if self.user_id is not None and self.role_id is not None:
            raise PermissionConflictingTarget(data_info="User ID e Role ID")
        if self.resource_id < -1 or self.resource_id == 0:
            raise ValueError("Permissão com resource_id inválido")
        if not self.actions:
            raise ValueError("Permissão deve ter pelo menos uma ação")

        unique_actions: list[PermissionAction] = []
        for action in self.actions:
            if action not in unique_actions:
                unique_actions.append(action)
        self.actions = unique_actions

        return self

    @model_validator(mode="after")
    def check_action_resource_consistency(self) -> Self:
        if self.resource == Resource.COURSE:
            invalid_actions = [
                action for action in self.actions if action not in CourseAction
            ]
            if invalid_actions:
                raise ValueError("Ação inválida para cursos")
        if self.resource == Resource.CLASSROOM:
            invalid_actions = [
                action for action in self.actions if action not in ClassroomAction
            ]
            if invalid_actions:
                raise ValueError("Ação inválida para recurso salas")
        return self


class PermissionUpdate(PermissionRegister):
    pass


class PermissionBatchRegister(BaseModel):
    permissions: list[PermissionRegister]


class PermissionMissingTarget(HTTPException):
    def __init__(self, data_info: str) -> None:
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            f"Permissão deve ter {data_info} definido",
        )


class PermissionConflictingTarget(HTTPException):
    def __init__(self, data_info: str) -> None:
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            f"Permissão não pode ter {data_info} definido ao mesmo tempo",
        )
