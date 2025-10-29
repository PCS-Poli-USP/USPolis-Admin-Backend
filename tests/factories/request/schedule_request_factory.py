from typing import Unpack
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.reservation_db_model import Reservation
from server.models.dicts.requests.schedule_requests_dicts import (
    ScheduleRegisterDict,
    ScheduleUpdateDict,
)
from server.models.http.requests.schedule_request_models import (
    ScheduleRegister,
    ScheduleUpdate,
)
from server.utils.enums.week_day import WeekDay
from server.utils.must_be_int import must_be_int
from tests.factories.base.schedule_base_factory import ScheduleBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory


class ScheduleRequestFactory(BaseRequestFactory):
    def __init__(
        self,
        classroom: Classroom | None = None,
        class_: Class | None = None,
        reservation: Reservation | None = None,
    ) -> None:
        super().__init__()
        self.core_factory = ScheduleBaseFactory()
        self.faker = self.core_factory.faker
        self.classroom = classroom
        self.class_ = class_
        self.reservation = reservation

    def get_default_create(self) -> ScheduleRegisterDict:
        """Get default values for creating a ScheduleRegister. The default values are:\n
        - class_id if a Class is passed on constructor else None
        - reservation_id if a Reservation is passed on constructor else None
        - classroom_id if a Classroom is passed on constructor else None
        - week_day is selected random on workdays (Monday - Friday)
        - month_week is None
        - dates is None
        """
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "class_id": must_be_int(self.class_.id) if self.class_ else None,
            "reservation_id": must_be_int(self.reservation.id)
            if self.reservation
            else None,
            "classroom_id": must_be_int(self.classroom.id) if self.classroom else None,
            "week_day": self.faker.random_element(WeekDay.workdays()),
            "month_week": None,
            "dates": None,
        }

    def get_default_update(self) -> ScheduleUpdateDict:
        """Get default values for creating a ScheduleUpdate.\n
        The values are the same as the ScheduleRegister
        """
        return self.get_default_create()

    def create_input(
        self, **overrides: Unpack[ScheduleRegisterDict]
    ) -> ScheduleRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return ScheduleRegister(**default)

    def update_input(self, **overrides: Unpack[ScheduleUpdateDict]) -> ScheduleUpdate:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return ScheduleUpdate(**default)
