from datetime import date, time

import pytest

from server.models.database.occurrence_db_model import Occurrence
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay
from server.utils.occurrence_utils import OccurrenceUtils
from tests.utils.time_test_utils import make_class_with_holidays, make_schedule


class TestDatesForRecurrence:
    def test_weekly_generates_one_date_per_week_on_the_target_weekday(self) -> None:
        dates = OccurrenceUtils._dates_for_recurrence(
            WeekDay.TUESDAY.value,
            Recurrence.WEEKLY,
            date(2025, 1, 1),
            date(2025, 1, 31),
        )
        assert dates == [
            date(2025, 1, 7),
            date(2025, 1, 14),
            date(2025, 1, 21),
            date(2025, 1, 28),
        ]
        assert all(d.weekday() == WeekDay.TUESDAY.value for d in dates)

    def test_biweekly_generates_one_date_every_two_weeks(self) -> None:
        dates = OccurrenceUtils._dates_for_recurrence(
            WeekDay.TUESDAY.value,
            Recurrence.BIWEEKLY,
            date(2025, 1, 1),
            date(2025, 2, 28),
        )
        assert dates == [
            date(2025, 1, 7),
            date(2025, 1, 21),
            date(2025, 2, 4),
            date(2025, 2, 18),
        ]

    def test_monthly_generates_one_date_per_month_for_the_given_month_week(
        self,
    ) -> None:
        dates = OccurrenceUtils._dates_for_recurrence(
            WeekDay.MONDAY.value,
            Recurrence.MONTHLY,
            date(2025, 1, 1),
            date(2025, 3, 31),
            MonthWeek.FIRST.value,
        )
        assert dates == [date(2025, 1, 6), date(2025, 2, 3), date(2025, 3, 3)]

    def test_monthly_without_month_week_raises(self) -> None:
        with pytest.raises(ValueError, match="Month week is required"):
            OccurrenceUtils._dates_for_recurrence(
                WeekDay.MONDAY.value,
                Recurrence.MONTHLY,
                date(2025, 1, 1),
                date(2025, 3, 31),
            )

    def test_daily_generates_every_weekday_and_skips_weekends(self) -> None:
        # 2025-01-06 is a Monday, 2025-01-12 is the following Sunday.
        dates = OccurrenceUtils._dates_for_recurrence(
            -1,
            Recurrence.DAILY,
            date(2025, 1, 6),
            date(2025, 1, 12),
        )
        assert dates == [
            date(2025, 1, 6),
            date(2025, 1, 7),
            date(2025, 1, 8),
            date(2025, 1, 9),
            date(2025, 1, 10),
        ]
        assert all(d.weekday() < 5 for d in dates)

    def test_custom_recurrence_returns_no_dates_from_dates_for_recurrence(
        self,
    ) -> None:
        # CUSTOM is handled by generate_dates/generate_occurrences before
        # reaching _dates_for_recurrence, whose match has no CUSTOM case.
        dates = OccurrenceUtils._dates_for_recurrence(
            WeekDay.MONDAY.value,
            Recurrence.CUSTOM,
            date(2025, 1, 1),
            date(2025, 1, 31),
        )
        assert dates == []


class TestDatesForRecurrenceEmptyResults:
    """Input combinations that are valid (no exception) but legitimately
    generate zero dates, as opposed to the error cases in
    TestDatesForRecurrence (e.g. missing month_week)."""

    def test_weekly_returns_empty_when_the_window_is_narrower_than_a_week(
        self,
    ) -> None:
        # 2025-01-01 is a Wednesday; the next Monday only falls on 2025-01-06,
        # past the single-day window below.
        dates = OccurrenceUtils._dates_for_recurrence(
            WeekDay.MONDAY.value,
            Recurrence.WEEKLY,
            date(2025, 1, 1),
            date(2025, 1, 1),
        )
        assert dates == []

    def test_biweekly_returns_empty_when_the_window_is_narrower_than_a_week(
        self,
    ) -> None:
        dates = OccurrenceUtils._dates_for_recurrence(
            WeekDay.MONDAY.value,
            Recurrence.BIWEEKLY,
            date(2025, 1, 1),
            date(2025, 1, 1),
        )
        assert dates == []

    def test_monthly_returns_empty_when_the_target_week_day_falls_outside_the_window(
        self,
    ) -> None:
        # The first Monday of January 2025 is 2025-01-06, outside this
        # narrow start/end window - and the loop only visits January once
        # before start_date+1 month already exceeds end_date.
        dates = OccurrenceUtils._dates_for_recurrence(
            WeekDay.MONDAY.value,
            Recurrence.MONTHLY,
            date(2025, 1, 1),
            date(2025, 1, 3),
            MonthWeek.FIRST.value,
        )
        assert dates == []

    def test_daily_returns_empty_when_the_window_only_covers_a_weekend(self) -> None:
        # 2025-01-04 is a Saturday, 2025-01-05 is a Sunday.
        dates = OccurrenceUtils._dates_for_recurrence(
            -1,
            Recurrence.DAILY,
            date(2025, 1, 4),
            date(2025, 1, 5),
        )
        assert dates == []

    @pytest.mark.parametrize(
        ("recurrence", "week_day", "month_week"),
        [
            (Recurrence.WEEKLY, WeekDay.MONDAY.value, None),
            (Recurrence.BIWEEKLY, WeekDay.MONDAY.value, None),
            (Recurrence.DAILY, -1, None),
            (Recurrence.MONTHLY, WeekDay.MONDAY.value, MonthWeek.FIRST.value),
        ],
    )
    def test_returns_empty_for_an_inverted_date_range(
        self, recurrence: Recurrence, week_day: int, month_week: int | None
    ) -> None:
        # start_date after end_date: every recurrence's while loop condition
        # is false on the first check, so this quietly yields no dates
        # rather than raising - worth locking in as documented behavior.
        dates = OccurrenceUtils._dates_for_recurrence(
            week_day,
            recurrence,
            date(2025, 1, 31),
            date(2025, 1, 1),
            month_week,
        )
        assert dates == []


class TestGetWeekdayDateForMonthWeek:
    def test_first_week_day_of_month(self) -> None:
        assert OccurrenceUtils.get_weekday_date_for_month_week(
            2025, 1, WeekDay.MONDAY.value, MonthWeek.FIRST.value
        ) == date(2025, 1, 6)

    def test_second_week_day_of_month(self) -> None:
        assert OccurrenceUtils.get_weekday_date_for_month_week(
            2025, 1, WeekDay.MONDAY.value, MonthWeek.SECOND.value
        ) == date(2025, 1, 13)

    def test_last_week_day_when_the_weekday_occurs_five_times(self) -> None:
        # March 2025 has 5 Mondays (3, 10, 17, 24, 31): no overflow correction needed.
        assert OccurrenceUtils.get_weekday_date_for_month_week(
            2025, 3, WeekDay.MONDAY.value, MonthWeek.LAST.value
        ) == date(2025, 3, 31)

    def test_last_week_day_when_the_weekday_occurs_only_four_times(self) -> None:
        # January 2025 has only 4 Mondays (6, 13, 20, 27): a naive +4 weeks
        # from the first Monday overflows into February, so the 5th Monday
        # doesn't exist and the result must fall back to the 4th one.
        assert OccurrenceUtils.get_weekday_date_for_month_week(
            2025, 1, WeekDay.MONDAY.value, MonthWeek.LAST.value
        ) == date(2025, 1, 27)

    def test_last_week_day_overflowing_across_a_year_boundary(self) -> None:
        # December 2025 has only 4 Thursdays (4, 11, 18, 25): a naive +4
        # weeks from the first Thursday overflows into January 2026,
        # exercising the `last_week_day_date.month == 1 and month == 12`
        # wraparound branch specifically (the plain "overflowed into next
        # month" check alone wouldn't catch a January-vs-December mismatch).
        assert OccurrenceUtils.get_weekday_date_for_month_week(
            2025, 12, WeekDay.THURSDAY.value, MonthWeek.LAST.value
        ) == date(2025, 12, 25)


class TestGenerateDates:
    def test_custom_recurrence_returns_dates_from_existing_occurrences(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.CUSTOM,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )
        schedule.occurrences = [
            Occurrence(date=date(2025, 1, 3), start_time=time(8, 0), end_time=time(9, 0)),
            Occurrence(date=date(2025, 1, 10), start_time=time(8, 0), end_time=time(9, 0)),
        ]
        assert OccurrenceUtils.generate_dates(schedule) == [
            date(2025, 1, 3),
            date(2025, 1, 10),
        ]

    def test_non_custom_recurrence_delegates_to_dates_for_recurrence(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.TUESDAY,
        )
        assert OccurrenceUtils.generate_dates(schedule) == [
            date(2025, 1, 7),
            date(2025, 1, 14),
            date(2025, 1, 21),
            date(2025, 1, 28),
        ]

    def test_daily_recurrence_works_without_a_week_day(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.DAILY,
            start_date=date(2025, 1, 6),
            end_date=date(2025, 1, 8),
            week_day=None,
        )
        assert OccurrenceUtils.generate_dates(schedule) == [
            date(2025, 1, 6),
            date(2025, 1, 7),
            date(2025, 1, 8),
        ]

    def test_custom_recurrence_returns_empty_when_there_are_no_occurrences(
        self,
    ) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.CUSTOM,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )
        schedule.occurrences = []
        assert OccurrenceUtils.generate_dates(schedule) == []

    def test_weekly_returns_empty_when_the_window_cannot_fit_the_week_day(
        self,
    ) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 1),
            week_day=WeekDay.MONDAY,
        )
        assert OccurrenceUtils.generate_dates(schedule) == []


class TestGenerateOccurrences:
    def test_raises_when_week_day_is_missing_for_a_weekly_schedule(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=None,
        )
        with pytest.raises(ValueError, match="Week day is required"):
            OccurrenceUtils.generate_occurrences(schedule)

    def test_custom_recurrence_builds_occurrences_from_existing_ones(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.CUSTOM,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )
        schedule.occurrences = [
            Occurrence(date=date(2025, 1, 3), start_time=time(8, 0), end_time=time(9, 0)),
        ]
        occurrences = OccurrenceUtils.generate_occurrences(schedule)
        assert len(occurrences) == 1
        assert occurrences[0].date == date(2025, 1, 3)
        assert occurrences[0].schedule is schedule

    def test_builds_one_occurrence_per_generated_date(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.TUESDAY,
            start_time=time(8, 0),
            end_time=time(10, 0),
        )
        occurrences = OccurrenceUtils.generate_occurrences(schedule)
        assert [o.date for o in occurrences] == [
            date(2025, 1, 7),
            date(2025, 1, 14),
            date(2025, 1, 21),
            date(2025, 1, 28),
        ]
        assert all(o.start_time == time(8, 0) for o in occurrences)
        assert all(o.end_time == time(10, 0) for o in occurrences)

    def test_excludes_dates_that_fall_on_a_holiday(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            week_day=WeekDay.TUESDAY,
        )
        schedule.class_ = make_class_with_holidays(holiday_dates=[date(2025, 1, 14)])

        occurrences = OccurrenceUtils.generate_occurrences(schedule)

        assert date(2025, 1, 14) not in [o.date for o in occurrences]
        assert [o.date for o in occurrences] == [
            date(2025, 1, 7),
            date(2025, 1, 21),
            date(2025, 1, 28),
        ]

    def test_returns_empty_when_every_generated_date_is_a_holiday(self) -> None:
        # Only one Tuesday falls in this window (2025-01-07), and it's a
        # holiday - dates was non-empty, but occurrences ends up empty.
        schedule = make_schedule(
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 7),
            week_day=WeekDay.TUESDAY,
        )
        schedule.class_ = make_class_with_holidays(holiday_dates=[date(2025, 1, 7)])

        assert OccurrenceUtils.generate_dates(schedule) == [date(2025, 1, 7)]
        assert OccurrenceUtils.generate_occurrences(schedule) == []

    def test_custom_recurrence_returns_empty_when_there_are_no_occurrences(
        self,
    ) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.CUSTOM,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )
        schedule.occurrences = []
        assert OccurrenceUtils.generate_occurrences(schedule) == []
