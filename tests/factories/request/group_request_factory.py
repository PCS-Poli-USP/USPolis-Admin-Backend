from server.models.dicts.requests.group_requests_dicts import (
    GroupRegisterDict,
    GroupUpdateDict,
)
from server.models.http.requests.group_request_models import GroupRegister, GroupUpdate
from tests.factories.request.base_request_factory import BaseRequestFactory


class GroupRequestFactory(BaseRequestFactory):
    def get_default_create(self) -> GroupRegisterDict:
        """Get default values for creating a BuildingRegister."""
        return {
            "name": self.faker.company(),
            "classroom_ids": [],
            "user_ids": [],
        }

    def get_default_update(self) -> GroupUpdateDict:
        """Get default values for creating a BuildingUpdate."""
        return self.get_default_create()

    def create_input(self, **overrides: GroupRegisterDict) -> GroupRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return GroupRegister(**default)

    def update_input(self, **overrides: GroupUpdateDict) -> GroupUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return GroupUpdate(**default)
