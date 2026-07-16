from server.models.dicts.base.role_base_dict import RoleBaseDict
from server.utils.enums.resources_enums import Resource
from tests.factories.base.base_factory import BaseFactory


class RoleBaseFactory(BaseFactory):
    """Base factory for role model or role request."""

    def __init__(self, resources: list[Resource] | None = None) -> None:
        super().__init__()
        self.resources = resources if resources is not None else []

    def get_base_defaults(self) -> RoleBaseDict:
        """Return base default values common to models and requests"""
        return {
            "name": self.faker.unique.job(),
            "description": self.faker.sentence(),
            "resources": self.resources,
        }
