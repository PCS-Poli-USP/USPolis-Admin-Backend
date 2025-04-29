from server.models.dicts.base.building_base_dict import BuildingBaseDict
from tests.factories.base.base_factory import BaseFactory


class BuildingBaseFactory(BaseFactory):
    """Base factory for building model or building request."""

    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> BuildingBaseDict:
        """Return base default values common to models and requests"""
        return {"name": self.faker.company()}
