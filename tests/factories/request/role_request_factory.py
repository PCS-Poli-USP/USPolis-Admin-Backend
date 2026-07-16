from typing import Unpack

from server.models.dicts.requests.role_requests_dicts import (
    RoleRegisterDict,
    RoleUpdateDict,
)
from server.models.http.requests.permission_request_models import PermissionRegister
from server.models.http.requests.role_request_models import RoleRegister, RoleUpdate
from server.utils.enums.actions_enums import PermissionAction
from server.utils.enums.resources_enums import Resource
from tests.factories.base.permission_base_factory import DEFAULT_ACTIONS_BY_RESOURCE
from tests.factories.base.role_base_factory import RoleBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory

# A role does not exist yet while its RoleRegister payload is being built, so
# nested permissions carry a placeholder role_id: the repository overwrites it
# with the persisted role's id once the role is created.
PLACEHOLDER_ROLE_ID = 0


class RoleRequestFactory(BaseRequestFactory):
    def __init__(self, resources: list[Resource] | None = None) -> None:
        super().__init__()
        self.core_factory = RoleBaseFactory(resources=resources)

    def build_permission(
        self,
        resource: Resource,
        resource_id: int = -1,
        actions: list[PermissionAction] | None = None,
    ) -> PermissionRegister:
        """Build a PermissionRegister to nest inside a RoleRegister/RoleUpdate payload."""
        return PermissionRegister(
            resource=resource,
            resource_id=resource_id,
            actions=actions or list(DEFAULT_ACTIONS_BY_RESOURCE[resource]),
            role_id=PLACEHOLDER_ROLE_ID,
        )

    def get_default_create(self) -> RoleRegisterDict:
        """Get default values for creating a RoleRegister."""
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "permissions": [],
        }

    def get_default_update(self) -> RoleUpdateDict:
        """Get default values for creating a RoleUpdate."""
        return self.get_default_create()

    def create_input(self, **overrides: Unpack[RoleRegisterDict]) -> RoleRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return RoleRegister(**default)

    def update_input(self, **overrides: Unpack[RoleUpdateDict]) -> RoleUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return RoleUpdate(**default)
