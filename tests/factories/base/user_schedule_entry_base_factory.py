from server.models.dicts.base.user_schedule_entry_base_dict import (
    UserScheduleEntryBaseDict,
)
from tests.factories.base.base_factory import BaseFactory


class UserScheduleEntryBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> UserScheduleEntryBaseDict:
        return {
            "absence_count": 0,
        }
