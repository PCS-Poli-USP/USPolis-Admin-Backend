from datetime import datetime, time

import pytest

from server.models.http.requests.class_request_models import (
    ClassInvalidData,
    ClassRegister,
    ClassUpdate,
)
from server.models.http.requests.schedule_request_models import (
    ScheduleRegister,
    ScheduleUpdate,
)
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.class_type import ClassType
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


def _base_kwargs() -> dict:
    return {
        "calendar_ids": [],
        "start_date": datetime(2025, 1, 1),
        "end_date": datetime(2025, 6, 30),
        "code": "T01",
        "type": ClassType.THEORIC,
        "professors": [],
        "vacancies": 40,
        "air_conditionating": False,
        "accessibility": True,
        "audiovisual": AudiovisualType.NONE,
        "ignore_to_allocate": False,
    }


def _schedule_register() -> ScheduleRegister:
    return ScheduleRegister(
        start_date=datetime(2025, 1, 1).date(),
        end_date=datetime(2025, 6, 30).date(),
        start_time=time(8, 0),
        end_time=time(10, 0),
        recurrence=Recurrence.WEEKLY,
        week_day=WeekDay.MONDAY,
    )


class TestClassRegister:
    def test_valid_input_passes(self) -> None:
        class_ = ClassRegister(
            subject_id=1, schedules_data=[_schedule_register()], **_base_kwargs()
        )

        assert class_.subject_id == 1

    def test_rejects_a_non_positive_subject_id(self) -> None:
        with pytest.raises(ClassInvalidData):
            ClassRegister(
                subject_id=0, schedules_data=[_schedule_register()], **_base_kwargs()
            )

    def test_rejects_no_schedules(self) -> None:
        with pytest.raises(ClassInvalidData):
            ClassRegister(subject_id=1, schedules_data=[], **_base_kwargs())


class TestClassUpdate:
    def test_rejects_a_non_positive_subject_id(self) -> None:
        schedule = ScheduleUpdate(**_schedule_register().model_dump())
        with pytest.raises(ClassInvalidData):
            ClassUpdate(subject_id=0, schedules_data=[schedule], **_base_kwargs())

    def test_rejects_no_schedules(self) -> None:
        with pytest.raises(ClassInvalidData):
            ClassUpdate(subject_id=1, schedules_data=[], **_base_kwargs())
