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
    def create_input(
        self, **overrides: Unpack[BuildingRegisterDict]
    ) -> BuildingRegister:
        default: BuildingRegisterDict = {
            "name": self.faker.name(),
        }
        self.update_default_dict(default, overrides)  # type: ignore
        return BuildingRegister(**default)

    def update_input(self, **overrides: Unpack[BuildingUpdateDict]) -> BuildingUpdate:
        default: BuildingUpdateDict = {
            "name": self.faker.name(),
        }
        self.update_default_dict(default, overrides)  # type: ignore
        return BuildingUpdate(**default)
