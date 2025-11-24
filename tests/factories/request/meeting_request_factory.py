from typing import Unpack
from server.models.dicts.requests.meeting_requests_dicts import (
    MeetingRegisterDict,
    MeetingUpdateDict,
)
from server.models.database.classroom_db_model import Classroom
from server.models.http.requests.meeting_request_models import (
    MeetingRegister,
    MeetingUpdate,
)
from server.utils.enums.reservation_type import ReservationType
from tests.factories.base.meeting_base_factory import MeetingBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory
from tests.factories.request.reservation_request_factory import (
    ReservationRequestFactory,
)


class MeetingRequestFactory(BaseRequestFactory):
    def __init__(self, classroom: Classroom) -> None:
        super().__init__()
        self.core_factory = MeetingBaseFactory()
        self.reservation_factory = ReservationRequestFactory(
            reservation_type=ReservationType.MEETING, classroom=classroom
        )
        self.classroom = classroom

    def get_default_create(self) -> MeetingRegisterDict:
        """Get default values for creating a MeetingRegister. The default values are:\n
        - link that have 50% of choice of be None or a url
        """
        core = self.core_factory.get_base_defaults()
        reservation_data = self.reservation_factory.get_default_create()
        return {
            **core,
            **reservation_data,
        }

    def get_default_update(self) -> MeetingUpdateDict:
        """Get default values for creating a MeetingUpdate. The default values are:\n
        - class_ids come from the classes passed
        """
        core = self.core_factory.get_base_defaults()
        reservation_data = self.reservation_factory.get_default_update()
        return {
            **core,
            **reservation_data,
        }

    def create_input(self, **overrides: Unpack[MeetingRegisterDict]) -> MeetingRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return MeetingRegister(**default)

    def update_input(self, **overrides: Unpack[MeetingUpdateDict]) -> MeetingUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return MeetingUpdate(**default)
