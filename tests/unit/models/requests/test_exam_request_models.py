from datetime import date, time

import pytest
from pydantic import ValidationError

from server.models.http.requests.exam_request_models import ExamRegister, ExamUpdate
from server.models.http.requests.schedule_request_models import (
    ScheduleRegister,
    ScheduleUpdate,
)
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


def _custom_schedule() -> ScheduleRegister:
    return ScheduleRegister(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 1),
        start_time=time(8, 0),
        end_time=time(10, 0),
        recurrence=Recurrence.CUSTOM,
        dates=[date(2025, 3, 10)],
    )


def _weekly_schedule() -> ScheduleRegister:
    return ScheduleRegister(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 6, 30),
        start_time=time(8, 0),
        end_time=time(10, 0),
        recurrence=Recurrence.WEEKLY,
        week_day=WeekDay.MONDAY,
    )


class TestExamRegister:
    def test_valid_input_passes(self) -> None:
        exam = ExamRegister(
            subject_id=1,
            title="Prova 1",
            reason=None,
            classroom_id=1,
            schedule_data=_custom_schedule(),
        )

        assert exam.subject_id == 1

    def test_rejects_a_non_custom_recurrence(self) -> None:
        with pytest.raises(ValidationError, match="custom recurrence"):
            ExamRegister(
                subject_id=1,
                title="Prova 1",
                reason=None,
                classroom_id=1,
                schedule_data=_weekly_schedule(),
            )

    def test_rejects_custom_recurrence_without_dates(self) -> None:
        schedule = _custom_schedule()
        schedule.dates = []
        with pytest.raises(ValidationError, match="an occurrence"):
            ExamRegister(
                subject_id=1,
                title="Prova 1",
                reason=None,
                classroom_id=1,
                schedule_data=schedule,
            )


class TestExamUpdate:
    def test_rejects_a_non_custom_recurrence(self) -> None:
        schedule = ScheduleUpdate(**_weekly_schedule().model_dump())
        with pytest.raises(ValidationError, match="custom recurrence"):
            ExamUpdate(
                subject_id=1,
                title="Prova 1",
                reason=None,
                classroom_id=1,
                schedule_data=schedule,
            )
