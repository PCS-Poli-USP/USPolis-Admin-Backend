from datetime import date, time

from server.models.database.occurrence_db_model import Occurrence
from server.models.http.requests.schedule_request_models import ScheduleUpdate
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay
from server.utils.schedule_utils import ScheduleUtils
from tests.utils.time_test_utils import make_schedule


def make_schedule_update(
    *,
    recurrence: Recurrence,
    start_date: date = date(2025, 1, 1),
    end_date: date = date(2025, 1, 31),
    start_time: time = time(8, 0),
    end_time: time = time(10, 0),
    week_day: WeekDay | None = None,
    month_week: MonthWeek | None = None,
    dates: list[date] | None = None,
) -> ScheduleUpdate:
    return ScheduleUpdate(
        start_date=start_date,
        end_date=end_date,
        start_time=start_time,
        end_time=end_time,
        recurrence=recurrence,
        week_day=week_day,
        month_week=month_week,
        dates=dates,
    )


class TestSortSchedules:
    def test_sorts_by_recurrence_then_start_time_then_end_time(self) -> None:
        weekly_late = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.MONDAY,
            start_time=time(14, 0),
            end_time=time(16, 0),
        )
        weekly_early = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.MONDAY,
            start_time=time(8, 0),
            end_time=time(10, 0),
        )
        daily = make_schedule(
            recurrence=Recurrence.DAILY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
        sorted_schedules = ScheduleUtils.sort_schedules(
            [weekly_late, daily, weekly_early]
        )
        assert sorted_schedules == [daily, weekly_early, weekly_late]


class TestSortSchedulesInput:
    def test_sorts_by_recurrence_then_start_time_then_end_time(self) -> None:
        weekly_late = make_schedule_update(
            recurrence=Recurrence.WEEKLY,
            week_day=WeekDay.MONDAY,
            start_time=time(14, 0),
        )
        weekly_early = make_schedule_update(
            recurrence=Recurrence.WEEKLY,
            week_day=WeekDay.MONDAY,
            start_time=time(8, 0),
        )
        daily = make_schedule_update(recurrence=Recurrence.DAILY, start_time=time(9, 0))

        sorted_inputs = ScheduleUtils.sort_schedules_input(
            [weekly_late, daily, weekly_early]
        )
        assert sorted_inputs == [daily, weekly_early, weekly_late]


class TestHasScheduleDiff:
    def test_false_when_nothing_changed(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.MONDAY,
            start_time=time(8, 0),
            end_time=time(10, 0),
        )
        schedule_input = make_schedule_update(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.MONDAY,
            start_time=time(8, 0),
            end_time=time(10, 0),
        )
        assert ScheduleUtils.has_schedule_diff(schedule, schedule_input) is False

    def test_true_when_recurrence_differs(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.MONDAY,
        )
        schedule_input = make_schedule_update(
            recurrence=Recurrence.BIWEEKLY,
            week_day=WeekDay.MONDAY,
        )
        assert ScheduleUtils.has_schedule_diff(schedule, schedule_input) is True

    def test_true_when_week_day_differs(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.MONDAY,
        )
        schedule_input = make_schedule_update(
            recurrence=Recurrence.WEEKLY,
            week_day=WeekDay.TUESDAY,
        )
        assert ScheduleUtils.has_schedule_diff(schedule, schedule_input) is True

    def test_true_when_month_week_differs(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.MONTHLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            week_day=WeekDay.MONDAY,
            month_week=MonthWeek.FIRST,
        )
        schedule_input = make_schedule_update(
            recurrence=Recurrence.MONTHLY,
            week_day=WeekDay.MONDAY,
            month_week=MonthWeek.SECOND,
        )
        assert ScheduleUtils.has_schedule_diff(schedule, schedule_input) is True

    def test_true_when_start_or_end_date_differs(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.MONDAY,
        )
        schedule_input = make_schedule_update(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 2, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.MONDAY,
        )
        assert ScheduleUtils.has_schedule_diff(schedule, schedule_input) is True

    def test_true_when_start_or_end_time_differs(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.MONDAY,
            start_time=time(8, 0),
        )
        schedule_input = make_schedule_update(
            recurrence=Recurrence.WEEKLY,
            week_day=WeekDay.MONDAY,
            start_time=time(9, 0),
        )
        assert ScheduleUtils.has_schedule_diff(schedule, schedule_input) is True

    def test_false_for_identical_custom_dates(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.CUSTOM,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )
        schedule.occurrences = [
            Occurrence(date=date(2025, 1, 3), start_time=time(8, 0), end_time=time(9, 0)),
            Occurrence(date=date(2025, 1, 10), start_time=time(8, 0), end_time=time(9, 0)),
        ]
        schedule_input = make_schedule_update(
            recurrence=Recurrence.CUSTOM,
            dates=[date(2025, 1, 3), date(2025, 1, 10)],
        )
        assert ScheduleUtils.has_schedule_diff(schedule, schedule_input) is False

    def test_true_when_custom_dates_count_differs(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.CUSTOM,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )
        schedule.occurrences = [
            Occurrence(date=date(2025, 1, 3), start_time=time(8, 0), end_time=time(9, 0)),
        ]
        schedule_input = make_schedule_update(
            recurrence=Recurrence.CUSTOM,
            dates=[date(2025, 1, 3), date(2025, 1, 10)],
        )
        assert ScheduleUtils.has_schedule_diff(schedule, schedule_input) is True

    def test_true_when_a_custom_date_differs(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.CUSTOM,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )
        schedule.occurrences = [
            Occurrence(date=date(2025, 1, 3), start_time=time(8, 0), end_time=time(9, 0)),
        ]
        schedule_input = make_schedule_update(
            recurrence=Recurrence.CUSTOM,
            dates=[date(2025, 1, 4)],
        )
        assert ScheduleUtils.has_schedule_diff(schedule, schedule_input) is True


class TestHasScheduleDiffFromList:
    def test_false_when_all_schedules_match(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.MONDAY,
        )
        schedule_input = make_schedule_update(
            recurrence=Recurrence.WEEKLY,
            week_day=WeekDay.MONDAY,
        )
        assert (
            ScheduleUtils.has_schedule_diff_from_list([schedule], [schedule_input])
            is False
        )

    def test_true_when_lengths_differ(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.MONDAY,
        )
        assert ScheduleUtils.has_schedule_diff_from_list([schedule], []) is True

    def test_true_when_any_schedule_in_the_list_differs(self) -> None:
        matching = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.MONDAY,
        )
        different = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.TUESDAY,
        )
        matching_input = make_schedule_update(
            recurrence=Recurrence.WEEKLY, week_day=WeekDay.MONDAY
        )
        different_input = make_schedule_update(
            recurrence=Recurrence.WEEKLY, week_day=WeekDay.MONDAY
        )
        assert (
            ScheduleUtils.has_schedule_diff_from_list(
                [matching, different], [matching_input, different_input]
            )
            is True
        )
