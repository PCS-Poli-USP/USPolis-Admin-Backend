from datetime import timedelta

from server.models.dicts.base.institutional_event_base_dict import (
    InstitutionalEventBaseDict,
)
from tests.factories.base.base_factory import BaseFactory


class InstitutionalEventBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_base_defaults(self) -> InstitutionalEventBaseDict:
        start = self.faker.date_time_between(start_date="now", end_date="+300d")
        return {
            "title": self.faker.sentence(nb_words=3),
            "description": self.faker.sentence(),
            "category": self.faker.word(),
            "start": start,
            "end": start + timedelta(hours=2),
            "location": None,
            "building": None,
            "classroom": None,
            "external_link": None,
        }
