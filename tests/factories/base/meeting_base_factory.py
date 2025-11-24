from random import choice
from server.models.dicts.base.meeting_base_dict import MeetingBaseDict
from tests.factories.base.base_factory import BaseFactory


class MeetingBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> MeetingBaseDict:
        return {
            "link": choice([self.faker.url(), None]),
        }
