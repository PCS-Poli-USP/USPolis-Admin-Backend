from datetime import date

from server.models.dicts.base.holiday_category_base_dict import HolidayCategoryBaseDict
from tests.factories.base.base_factory import BaseFactory


class HolidayCategoryBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> HolidayCategoryBaseDict:
        return {
            "name": self.faker.unique.word(),
            "year": date.today().year,
        }
