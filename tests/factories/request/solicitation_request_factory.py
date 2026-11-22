from typing import Unpack

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.dicts.requests.solicitation_requests_dicts import (
    SolicitationRegisterDict,
)
from server.models.http.requests.solicitation_request_models import (
    MeetingSolicitation,
    SolicitationRegister,
)
from server.utils.must_be_int import must_be_int
from tests.factories.base.solicitation_base_factory import SolicitationBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory
from tests.factories.request.meeting_request_factory import MeetingRequestFactory


class SolicitationRequestFactory(BaseRequestFactory):
    """A solicitation of a meeting in `classroom` of `building`."""

    def __init__(self, building: Building, classroom: Classroom) -> None:
        super().__init__()
        self.core_factory = SolicitationBaseFactory(must_be_int(building.id))
        self.building = building
        self.classroom = classroom

    def get_default_create(self) -> SolicitationRegisterDict:
        """Get default values for creating a SolicitationRegister. The default
        values are:\n
        - reservation_data is a meeting (MeetingRequestFactory) in `classroom`
        """
        core = self.core_factory.get_base_defaults()
        meeting = MeetingRequestFactory(self.classroom).create_input().model_dump()
        meeting["classroom_id"] = self.classroom.id
        return {
            **core,
            "reservation_data": MeetingSolicitation(**meeting),
        }

    def create_input(
        self, **overrides: Unpack[SolicitationRegisterDict]
    ) -> SolicitationRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return SolicitationRegister(**default)
