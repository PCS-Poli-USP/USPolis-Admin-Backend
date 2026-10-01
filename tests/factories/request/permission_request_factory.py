from typing import Unpack

from server.models.database.role_db_model import Role
from server.models.dicts.requests.permission_requests_dicts import (
    PermissionRegisterDict,
    PermissionUpdateDict,
)
from server.models.http.requests.permission_request_models import (
    PermissionRegister,
    PermissionUpdate,
)
from server.utils.enums.resources_enums import Resource
from server.utils.must_be_int import must_be_int
from tests.factories.base.permission_base_factory import PermissionBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory


class PermissionRequestFactory(BaseRequestFactory):
    """Factory for building PermissionRegister/PermissionUpdate payloads for an existing role.\n
    Use `role_id` directly instead when the target role has not been persisted yet
    (e.g. permissions nested inside a RoleRegister payload).
    """

    def __init__(self, role: Role, resource: Resource = Resource.CLASSROOM) -> None:
        super().__init__()
        self.role = role
        self.core_factory = PermissionBaseFactory(
            role_id=must_be_int(role.id), resource=resource
        )

    def get_default_create(self) -> PermissionRegisterDict:
        """Get default values for creating a PermissionRegister."""
        core = self.core_factory.get_base_defaults()
        return {**core}

    def get_default_update(self) -> PermissionUpdateDict:
        """Get default values for creating a PermissionUpdate."""
        return self.get_default_create()

    def create_input(
        self, **overrides: Unpack[PermissionRegisterDict]
    ) -> PermissionRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return PermissionRegister(**default)

    def update_input(
        self, **overrides: Unpack[PermissionUpdateDict]
    ) -> PermissionUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return PermissionUpdate(**default)
