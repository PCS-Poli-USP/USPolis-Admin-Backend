from pydantic import BaseModel

from server.models.http.requests.permission_request_models import (
    PermissionRegister,
)
from server.utils.enums.resources_enums import Resource


class RoleRegister(BaseModel):
    name: str
    resources: list[Resource]
    description: str = ""

    permissions: list[PermissionRegister]


class RoleUpdate(RoleRegister):
    pass
