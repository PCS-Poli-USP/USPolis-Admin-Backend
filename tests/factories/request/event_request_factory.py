from typing import Unpack
from server.models.dicts.requests.event_requests_dicts import (
    EventRegisterDict,
    EventUpdateDict,
)
from server.models.http.requests.event_request_models import EventRegister, EventUpdate
from server.models.database.classroom_db_model import Classroom
from server.utils.enums.event_type_enum import EventType
from server.utils.enums.reservation_type import ReservationType
from tests.factories.base.event_base_factory import EventBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory
from tests.factories.request.reservation_request_factory import (
    ReservationRequestFactory,
)


class EventRequestFactory(BaseRequestFactory):
    def __init__(self, classroom: Classroom) -> None:
        super().__init__()
        self.core_factory = EventBaseFactory()
        self.reservation_factory = ReservationRequestFactory(
            reservation_type=ReservationType.EVENT, classroom=classroom
        )
        self.classroom = classroom
        self.faker = self.core_factory.faker

    def get_default_create(self) -> EventRegisterDict:
        """Get default values for creating a EventRegister. The default values are:\n
        - link that have 50% of choice of be None or a url
        """
        core = self.core_factory.get_base_defaults()
        reservation_data = self.reservation_factory.get_default_create()
        return {
            **core,
            **reservation_data,
            "event_type": self.faker.random_element(elements=EventType.values()),
        }

    def get_default_update(self) -> EventUpdateDict:
        """Get default values for creating EventUpdate. The default values are:\n
        - class_ids come from the classes passed
        """
        core = self.core_factory.get_base_defaults()
        reservation_data = self.reservation_factory.get_default_update()
        return {
            **core,
            **reservation_data,
            "event_type": self.faker.random_element(elements=EventType.values()),
        }

    def create_input(self, **overrides: Unpack[EventRegisterDict]) -> EventRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return EventRegister(**default)

    def update_input(self, **overrides: Unpack[EventUpdateDict]) -> EventUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return EventUpdate(**default)
