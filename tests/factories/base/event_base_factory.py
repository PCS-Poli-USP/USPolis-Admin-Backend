from random import choice
from server.models.dicts.base.event_base_dict import EventBaseDict
from tests.factories.base.base_factory import BaseFactory


class EventBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> EventBaseDict:
        return {
            "link": choice([self.faker.url(), None]),
        }
