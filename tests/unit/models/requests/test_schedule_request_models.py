from datetime import date, time

import pytest

from server.models.http.requests.schedule_request_models import (
    ScheduleConflictedData,
    ScheduleInvalidData,
    ScheduleRegister,
    ScheduleUpdate,
)
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay

_START = date(2025, 1, 1)
_END = date(2025, 6, 30)
_START_TIME = time(8, 0)
_END_TIME = time(10, 0)


def _base_kwargs() -> dict:
    return {
        "start_date": _START,
        "end_date": _END,
        "start_time": _START_TIME,
        "end_time": _END_TIME,
    }


class TestScheduleRegister:
    def test_valid_weekly_schedule_passes(self) -> None:
        schedule = ScheduleRegister(
            recurrence=Recurrence.WEEKLY, week_day=WeekDay.MONDAY, **_base_kwargs()
        )

        assert schedule.week_day == WeekDay.MONDAY

    def test_valid_daily_schedule_passes_without_week_day(self) -> None:
        schedule = ScheduleRegister(recurrence=Recurrence.DAILY, **_base_kwargs())

        assert schedule.week_day is None

    def test_valid_monthly_schedule_passes_with_month_week(self) -> None:
        schedule = ScheduleRegister(
            recurrence=Recurrence.MONTHLY,
            week_day=WeekDay.MONDAY,
            month_week=MonthWeek.FIRST,
            **_base_kwargs(),
        )

        assert schedule.month_week == MonthWeek.FIRST

    def test_valid_custom_schedule_passes_with_dates(self) -> None:
        schedule = ScheduleRegister(
            recurrence=Recurrence.CUSTOM,
            dates=[date(2025, 3, 10)],
            **_base_kwargs(),
        )

        assert schedule.dates == [date(2025, 3, 10)]

    def test_valid_allocated_schedule_passes_with_a_classroom(self) -> None:
        schedule = ScheduleRegister(
            recurrence=Recurrence.WEEKLY,
            week_day=WeekDay.MONDAY,
            allocated=True,
            classroom_id=1,
            **_base_kwargs(),
        )

        assert schedule.allocated is True

    def test_rejects_both_class_id_and_reservation_id(self) -> None:
        with pytest.raises(ScheduleConflictedData):
            ScheduleRegister(
                recurrence=Recurrence.WEEKLY,
                week_day=WeekDay.MONDAY,
                class_id=1,
                reservation_id=2,
                **_base_kwargs(),
            )

    def test_requires_week_day_for_non_custom_non_daily_recurrence(self) -> None:
        with pytest.raises(ScheduleInvalidData):
            ScheduleRegister(recurrence=Recurrence.WEEKLY, **_base_kwargs())

    def test_rejects_week_day_for_custom_recurrence(self) -> None:
        with pytest.raises(ScheduleInvalidData):
            ScheduleRegister(
                recurrence=Recurrence.CUSTOM,
                week_day=WeekDay.MONDAY,
                dates=[date(2025, 3, 10)],
                **_base_kwargs(),
            )

    def test_rejects_week_day_for_daily_recurrence(self) -> None:
        with pytest.raises(ScheduleInvalidData):
            ScheduleRegister(
                recurrence=Recurrence.DAILY,
                week_day=WeekDay.MONDAY,
                **_base_kwargs(),
            )

    def test_rejects_month_week_for_non_monthly_recurrence(self) -> None:
        with pytest.raises(ScheduleInvalidData):
            ScheduleRegister(
                recurrence=Recurrence.WEEKLY,
                week_day=WeekDay.MONDAY,
                month_week=MonthWeek.FIRST,
                **_base_kwargs(),
            )

    def test_requires_month_week_for_monthly_recurrence(self) -> None:
        with pytest.raises(ScheduleInvalidData):
            ScheduleRegister(
                recurrence=Recurrence.MONTHLY,
                week_day=WeekDay.MONDAY,
                **_base_kwargs(),
            )

    def test_rejects_dates_for_non_custom_recurrence(self) -> None:
        with pytest.raises(ScheduleInvalidData):
            ScheduleRegister(
                recurrence=Recurrence.WEEKLY,
                week_day=WeekDay.MONDAY,
                dates=[date(2025, 3, 10)],
                **_base_kwargs(),
            )

    def test_rejects_mismatched_labels_length(self) -> None:
        with pytest.raises(ScheduleInvalidData):
            ScheduleRegister(
                recurrence=Recurrence.CUSTOM,
                dates=[date(2025, 3, 10), date(2025, 3, 17)],
                labels=["Aula 1"],
                **_base_kwargs(),
            )

    def test_rejects_mismatched_times_length(self) -> None:
        with pytest.raises(ScheduleInvalidData):
            ScheduleRegister(
                recurrence=Recurrence.CUSTOM,
                dates=[date(2025, 3, 10), date(2025, 3, 17)],
                times=[(time(8, 0), time(10, 0))],
                **_base_kwargs(),
            )

    def test_rejects_allocated_without_a_classroom(self) -> None:
        with pytest.raises(ScheduleInvalidData):
            ScheduleRegister(
                recurrence=Recurrence.WEEKLY,
                week_day=WeekDay.MONDAY,
                allocated=True,
                **_base_kwargs(),
            )


class TestScheduleUpdate:
    def test_shares_the_same_validation_as_register(self) -> None:
        with pytest.raises(ScheduleInvalidData):
            ScheduleUpdate(recurrence=Recurrence.WEEKLY, **_base_kwargs())
