from server.models.dicts.base.group_base_dict import GroupBaseDict
from tests.factories.base.base_factory import BaseFactory


class GroupBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> GroupBaseDict:
        """Return base default values common to models and requests"""
        return {
            "name": self.faker.name(),
        }
