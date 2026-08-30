from server.models.dicts.base.intentional_conflict_base_dict import (
    IntentionalConflictBaseDict,
)
from tests.factories.base.base_factory import BaseFactory


class IntentionalConflictBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> IntentionalConflictBaseDict:
        return {}
