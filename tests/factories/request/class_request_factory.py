from datetime import datetime, time
from typing import Unpack

from server.models.database.subject_db_model import Subject
from server.models.dicts.requests.class_requests_dicts import (
    ClassRegisterDict,
    ClassUpdateDict,
)
from server.models.http.requests.class_request_models import ClassRegister, ClassUpdate
from server.utils.must_be_int import must_be_int
from tests.factories.base.class_base_factory import ClassBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory
from tests.factories.request.schedule_request_factory import ScheduleRequestFactory


class ClassRequestFactory(BaseRequestFactory):
    def __init__(self, subject: Subject) -> None:
        super().__init__()
        self.subject = subject
        self.core_factory = ClassBaseFactory()
        self.schedule_factory = ScheduleRequestFactory()

    def get_default_create(self) -> ClassRegisterDict:
        """Get default values for creating a ClassRegister. The default
        values are:\n
        - subject_id is the Subject passed
        - a single default schedule
        - no calendars
        """
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "start_date": datetime.combine(core["start_date"], time.min),
            "end_date": datetime.combine(core["end_date"], time.min),
            "subject_id": must_be_int(self.subject.id),
            "calendar_ids": [],
            "schedules_data": [self.schedule_factory.create_input()],
        }

    def get_default_update(self) -> ClassUpdateDict:
        core = self.get_default_create()
        return {
            **core,
            "schedules_data": [self.schedule_factory.update_input()],
        }

    def create_input(self, **overrides: Unpack[ClassRegisterDict]) -> ClassRegister:
        default: dict = dict(self.get_default_create())
        self.override_default_dict(default, overrides)  # type: ignore
        return ClassRegister(**default)

    def update_input(self, **overrides: Unpack[ClassUpdateDict]) -> ClassUpdate:
        default: dict = dict(self.get_default_update())
        self.override_default_dict(default, overrides)  # type: ignore
        return ClassUpdate(**default)
