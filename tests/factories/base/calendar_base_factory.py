from server.models.dicts.base.calendar_base_dict import CalendarBaseDict
from tests.factories.base.base_factory import BaseFactory


class CalendarBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> CalendarBaseDict:
        return {
            "name": self.faker.unique.word(),
            "year": int(self.faker.year()),
        }
