from typing import Unpack
from server.models.http.requests.exam_request_models import ExamRegister, ExamUpdate
from server.models.http.requests.schedule_request_models import ScheduleRegister
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.subject_db_model import Subject
from server.models.dicts.requests.exam_requests_dicts import (
    ExamUpdateDict,
    ExamRegisterDict,
)
from tests.factories.base.exam_base_factory import ExamBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory
from tests.factories.request.reservation_request_factory import (
    ReservationRequestFactory,
)


class ExamRequestFactory(BaseRequestFactory):
    def __init__(
        self, subject: Subject, classroom: Classroom, classes: list[Class] = []
    ) -> None:
        super().__init__()
        self.core_factory = ExamBaseFactory(must_be_int(subject.id))
        self.reservation_factory = ReservationRequestFactory(
            reservation_type=ReservationType.EXAM, classroom=classroom
        )
        self.schedule_factory = self.reservation_factory.schedule_factory
        self.subject = subject
        self.classes = classes
        self.classroom = classroom

    def format_schedule_data(self, schedule_data: ScheduleRegister) -> None:
        """Format schedule data to have correct recurrence, dates and week_day."""
        start = schedule_data.start_date
        end = schedule_data.end_date
        dates = self.schedule_factory.get_random_dates(start, end, 3)

        schedule_data.recurrence = Recurrence.CUSTOM
        schedule_data.dates = dates
        schedule_data.week_day = None

    def get_default_create(self) -> ExamRegisterDict:
        """Get default values for creating a ExamRegister. The default values are:\n
        - class_ids come from the classes passed
        """
        core = self.core_factory.get_base_defaults()
        reservation_data = self.reservation_factory.get_default_create()
        self.format_schedule_data(reservation_data["schedule_data"])  # pyright: ignore[reportTypedDictNotRequiredAccess]

        return {
            **core,
            **reservation_data,
            "class_ids": [must_be_int(c.id) for c in self.classes],
        }

    def get_default_update(self) -> ExamUpdateDict:
        """Get default values for creating a ExamUpdate. The default values are:\n
        - class_ids come from the classes passed
        """
        core = self.core_factory.get_base_defaults()
        reservation_data = self.reservation_factory.get_default_update()
        self.format_schedule_data(reservation_data["schedule_data"])  # pyright: ignore[reportTypedDictNotRequiredAccess]
        return {
            **core,
            **reservation_data,
            "class_ids": [must_be_int(c.id) for c in self.classes],
        }

    def create_input(self, **overrides: Unpack[ExamRegisterDict]) -> ExamRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return ExamRegister(**default)

    def update_input(self, **overrides: Unpack[ExamUpdateDict]) -> ExamUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return ExamUpdate(**default)
