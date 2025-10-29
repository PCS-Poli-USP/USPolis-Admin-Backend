from server.models.dicts.base.solicitation_base_dict import SolicitationBaseDict
from tests.factories.base.base_factory import BaseFactory


class SolicitationBaseFactory(BaseFactory):
    def __init__(self, building_id: int) -> None:
        super().__init__()
        self.building_id = building_id

    def get_base_defaults(self) -> SolicitationBaseDict:
        return {
            "capacity": self.faker.random_int(min=1, max=100),
            "required_classroom": self.faker.boolean(),
            "building_id": self.building_id,
        }
