from pydantic import BaseModel, Field

from server.models.http.requests.permission_request_models import (
    PermissionRegister,
)
from server.utils.enums.resources_enums import Resource


class RoleRegister(BaseModel):
    name: str
    resources: list[Resource]
    description: str = ""

    permissions_ids: list[tuple[int, Resource]] | None = None
    permissions: list[PermissionRegister] = Field(default_factory=list)


class RoleUpdate(RoleRegister):
    pass
