from datetime import datetime

from pydantic import BaseModel

from server.models.database.role_db_model import Role
from server.models.http.responses.permissions_response_models import (
    PermissionResponse,
)
from server.utils.enums.resources_enums import Resource
from server.utils.type_guard import TypeGuard


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str
    resources: list[Resource]
    permissions: list[PermissionResponse]

    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_role(cls, role: Role) -> "RoleResponse":
        permissions_map = role.get_resource_permissions_map()
        permissions: list[PermissionResponse] = []
        for resource, resource_permissions in permissions_map.items():
            permissions.extend(
                PermissionResponse.from_permissions(resource_permissions, resource)  # type: ignore
            )

        return cls(
            id=TypeGuard.must_be_int(role.id),
            name=role.name,
            description=role.description,
            resources=role.resources,
            permissions=permissions,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )

    @classmethod
    def from_roles(cls, roles: list[Role]) -> list["RoleResponse"]:
        return [cls.from_role(role) for role in roles]
