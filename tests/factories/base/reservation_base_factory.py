from server.models.dicts.base.reservation_base_dict import ReservationBaseDict
from server.utils.enums.reservation_type import ReservationType
from tests.factories.base.base_factory import BaseFactory


class ReservationBaseFactory(BaseFactory):
    def __init__(self, reservation_type: ReservationType) -> None:
        super().__init__()
        self.type = reservation_type

    def get_base_defaults(self) -> ReservationBaseDict:
        return {
            "title": self.faker.sentence(nb_words=5),
            "type": self.type,
            "reason": self.faker.paragraph(nb_sentences=2),
        }
