from datetime import time

from server.models.dicts.base.occurrence_base_dict import OccurrenceBaseDict
from tests.factories.base.base_factory import BaseFactory


class OccurrenceBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> OccurrenceBaseDict:
        return {
            "start_time": time(8, 0),
            "end_time": time(10, 0),
            "date": self.faker.date_between(start_date="today", end_date="+90d"),
        }
