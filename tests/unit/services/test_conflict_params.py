from datetime import date, time

import pytest

from server.services.conflict_checker import ConflictParams, InvalidConflictParams
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay

_START = date(2024, 3, 1)
_END = date(2024, 6, 1)


class TestConflictParamsNonCustomRecurrence:
    def test_valid_weekly_passes(self) -> None:
        params = ConflictParams(
            start_time=time(8, 0),
            end_time=time(10, 0),
            recurrence=Recurrence.WEEKLY,
            start_date=_START,
            end_date=_END,
            week_day=WeekDay.MONDAY,
        )

        assert params.recurrence == Recurrence.WEEKLY

    def test_valid_daily_passes_without_week_day(self) -> None:
        params = ConflictParams(
            start_time=time(8, 0),
            end_time=time(10, 0),
            recurrence=Recurrence.DAILY,
            start_date=_START,
            end_date=_END,
        )

        assert params.recurrence == Recurrence.DAILY

    def test_valid_monthly_passes_with_month_week(self) -> None:
        params = ConflictParams(
            start_time=time(8, 0),
            end_time=time(10, 0),
            recurrence=Recurrence.MONTHLY,
            start_date=_START,
            end_date=_END,
            week_day=WeekDay.MONDAY,
            month_week=MonthWeek.FIRST,
        )

        assert params.month_week == MonthWeek.FIRST

    def test_rejects_dates(self) -> None:
        with pytest.raises(InvalidConflictParams):
            ConflictParams(
                start_time=time(8, 0),
                end_time=time(10, 0),
                recurrence=Recurrence.WEEKLY,
                start_date=_START,
                end_date=_END,
                week_day=WeekDay.MONDAY,
                dates=[_START],
            )

    def test_rejects_times(self) -> None:
        with pytest.raises(InvalidConflictParams):
            ConflictParams(
                start_time=time(8, 0),
                end_time=time(10, 0),
                recurrence=Recurrence.WEEKLY,
                start_date=_START,
                end_date=_END,
                week_day=WeekDay.MONDAY,
                times=[(time(8, 0), time(9, 0))],
            )

    def test_requires_start_and_end_date(self) -> None:
        with pytest.raises(InvalidConflictParams):
            ConflictParams(
                start_time=time(8, 0),
                end_time=time(10, 0),
                recurrence=Recurrence.WEEKLY,
                week_day=WeekDay.MONDAY,
            )

    def test_rejects_week_day_on_daily(self) -> None:
        with pytest.raises(InvalidConflictParams):
            ConflictParams(
                start_time=time(8, 0),
                end_time=time(10, 0),
                recurrence=Recurrence.DAILY,
                start_date=_START,
                end_date=_END,
                week_day=WeekDay.MONDAY,
            )

    def test_requires_week_day_on_non_daily(self) -> None:
        with pytest.raises(InvalidConflictParams):
            ConflictParams(
                start_time=time(8, 0),
                end_time=time(10, 0),
                recurrence=Recurrence.WEEKLY,
                start_date=_START,
                end_date=_END,
            )

    def test_rejects_month_week_on_weekly(self) -> None:
        with pytest.raises(InvalidConflictParams):
            ConflictParams(
                start_time=time(8, 0),
                end_time=time(10, 0),
                recurrence=Recurrence.WEEKLY,
                start_date=_START,
                end_date=_END,
                week_day=WeekDay.MONDAY,
                month_week=MonthWeek.FIRST,
            )

    def test_requires_month_week_on_monthly(self) -> None:
        with pytest.raises(InvalidConflictParams):
            ConflictParams(
                start_time=time(8, 0),
                end_time=time(10, 0),
                recurrence=Recurrence.MONTHLY,
                start_date=_START,
                end_date=_END,
                week_day=WeekDay.MONDAY,
            )


class TestConflictParamsCustomRecurrence:
    def test_valid_custom_passes_with_dates(self) -> None:
        params = ConflictParams(
            start_time=time(8, 0),
            end_time=time(10, 0),
            recurrence=Recurrence.CUSTOM,
            dates=[_START, _END],
        )

        assert params.dates == [_START, _END]

    def test_requires_dates(self) -> None:
        with pytest.raises(InvalidConflictParams):
            ConflictParams(
                start_time=time(8, 0),
                end_time=time(10, 0),
                recurrence=Recurrence.CUSTOM,
            )

    def test_rejects_times_with_mismatched_length(self) -> None:
        with pytest.raises(InvalidConflictParams):
            ConflictParams(
                start_time=time(8, 0),
                end_time=time(10, 0),
                recurrence=Recurrence.CUSTOM,
                dates=[_START, _END],
                times=[(time(8, 0), time(9, 0))],
            )

    def test_rejects_a_time_pair_with_start_after_end(self) -> None:
        with pytest.raises(InvalidConflictParams):
            ConflictParams(
                start_time=time(8, 0),
                end_time=time(10, 0),
                recurrence=Recurrence.CUSTOM,
                dates=[_START],
                times=[(time(11, 0), time(9, 0))],
            )

    def test_accepts_matching_times_and_dates(self) -> None:
        params = ConflictParams(
            start_time=time(8, 0),
            end_time=time(10, 0),
            recurrence=Recurrence.CUSTOM,
            dates=[_START, _END],
            times=[(time(8, 0), time(9, 0)), (time(10, 0), time(11, 0))],
        )

        assert params.times == [(time(8, 0), time(9, 0)), (time(10, 0), time(11, 0))]
