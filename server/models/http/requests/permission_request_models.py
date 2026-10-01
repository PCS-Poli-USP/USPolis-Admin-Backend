from typing import Self

from pydantic import BaseModel, model_validator

from server.utils.enums.actions_enums import (
    BuildingAction,
    ClassroomAction,
    CourseAction,
    PermissionAction,
)
from server.utils.enums.resources_enums import Resource


class PermissionRegister(BaseModel):
    resource: Resource
    resource_id: int
    actions: list[PermissionAction]
    role_id: int

    @model_validator(mode="after")
    def check_permission_body(self) -> Self:
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
        if self.resource == Resource.BUILDING:
            invalid_actions = [
                action for action in self.actions if action not in BuildingAction
            ]
            if invalid_actions:
                raise ValueError("Ação inválida para recurso prédios")
        return self


class PermissionUpdate(PermissionRegister):
    pass


class PermissionBatchRegister(BaseModel):
    permissions: list[PermissionRegister]
