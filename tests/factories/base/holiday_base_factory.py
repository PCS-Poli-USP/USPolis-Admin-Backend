from server.models.dicts.base.holiday_base_dict import HolidayBaseDict
from tests.factories.base.base_factory import BaseFactory


class HolidayBaseFactory(BaseFactory):
    def __init__(self, category_id: int) -> None:
        super().__init__()
        self.category_id = category_id

    def get_base_defaults(self) -> HolidayBaseDict:
        return {
            "name": self.faker.unique.word(),
            "category_id": self.category_id,
        }
