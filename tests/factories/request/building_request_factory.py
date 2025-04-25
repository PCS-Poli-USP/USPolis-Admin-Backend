from typing import Unpack
from server.models.dicts.requests.building_requests_dicts import (
    BuildingRegisterDict,
    BuildingUpdateDict,
)
from server.models.http.requests.building_request_models import (
    BuildingRegister,
    BuildingUpdate,
)
from tests.factories.request.base_request_factory import BaseRequestFactory


class BuildingRequestFactory(BaseRequestFactory):
    def get_default_create(self) -> BuildingRegisterDict:
        """Get default values for creating a BuildingRegister."""
        return {
            "name": self.faker.company(),
        }

    def get_default_update(self) -> BuildingUpdateDict:
        """Get default values for creating a BuildingUpdate."""
        return self.get_default_create()

    def create_input(
        self, **overrides: Unpack[BuildingRegisterDict]
    ) -> BuildingRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return BuildingRegister(**default)

    def update_input(self, **overrides: Unpack[BuildingUpdateDict]) -> BuildingUpdate:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return BuildingUpdate(**default)
