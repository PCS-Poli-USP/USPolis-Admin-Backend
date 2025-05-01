from server.models.database.building_db_model import Building
from server.models.dicts.requests.group_requests_dicts import (
    GroupRegisterDict,
    GroupUpdateDict,
)
from server.models.http.requests.group_request_models import GroupRegister, GroupUpdate
from server.utils.must_be_int import must_be_int
from tests.factories.base.group_base_factory import GroupBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory


class GroupRequestFactory(BaseRequestFactory):
    def __init__(self, building: Building) -> None:
        super().__init__()
        self.building = building
        self.core_factory = GroupBaseFactory(building_id=must_be_int(building.id))

    def get_default_create(self) -> GroupRegisterDict:
        """Get default values for creating a BuildingRegister."""
        core = self.core_factory.get_base_defaults()
        return {
            **core,
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
