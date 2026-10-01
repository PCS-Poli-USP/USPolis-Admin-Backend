from server.models.dicts.base.allocation_log_base_dict import AllocationLogBaseDict
from server.utils.enums.action_type_enum import ActionType
from tests.factories.base.base_factory import BaseFactory


class AllocationLogBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> AllocationLogBaseDict:
        return {
            "user_email": self.faker.email(domain="usp.br"),
            "modified_by": self.faker.name(),
            "action": ActionType.ALLOCATE,
            "old_classroom": self.faker.word(),
            "old_building": self.faker.word(),
            "new_classroom": self.faker.word(),
            "new_building": self.faker.word(),
        }
