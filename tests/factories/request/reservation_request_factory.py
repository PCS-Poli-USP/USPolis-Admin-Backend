from typing import Unpack
from server.models.database.classroom_db_model import Classroom
from server.models.dicts.requests.reservation_requests_dicts import (
    ReservationRegisterDict,
    ReservationUpdateDict,
)
from server.models.http.requests.reservation_request_models import (
    ReservationRegister,
    ReservationUpdate,
)
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from tests.factories.base.reservation_base_factory import ReservationBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory
from tests.factories.request.schedule_request_factory import ScheduleRequestFactory


class ReservationRequestFactory(BaseRequestFactory):
    def __init__(self, reservation_type: ReservationType, classroom: Classroom) -> None:
        super().__init__()
        self.reservation_type = reservation_type
        self.core_factory = ReservationBaseFactory(reservation_type)
        self.schedule_factory = ScheduleRequestFactory(classroom=classroom)
        self.classroom = classroom

    def get_default_create(self) -> ReservationRegisterDict:
        """Get default values for creating a ReservationRegister. The default values are:\n
        - classroom_id is the Classroom passed
        - schedule_date is a default ScheduleRegister
        """
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "classroom_id": must_be_int(self.classroom.id),
            "schedule_data": self.schedule_factory.create_input(),
        }

    def get_default_update(self) -> ReservationUpdateDict:
        """Get default values for creating a ReservationUpdate. The default values are:\n
        - classroom_id is the Classroom passed
        - schedule_date is a default ScheduleUpdate
        """
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "classroom_id": must_be_int(self.classroom.id),
            "schedule_data": self.schedule_factory.update_input(),
        }

    def create_input(
        self, **overrides: Unpack[ReservationRegisterDict]
    ) -> ReservationRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return ReservationRegister(**default)

    def update_input(
        self, **overrides: Unpack[ReservationUpdateDict]
    ) -> ReservationUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return ReservationUpdate(**default)
