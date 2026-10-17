from datetime import date, timedelta

import pytest

from server.deps.interval_dep import (
    InvalidQueryInterval,
    QueryInterval,
    ensure_valid_span,
)


class TestQueryInterval:
    def test_defaults_to_today_when_nothing_given(self) -> None:
        interval = QueryInterval()

        assert interval.today == date.today()
        assert interval.start is None
        assert interval.end is None

    def test_accepts_an_explicit_today(self) -> None:
        today = date(2024, 3, 1)

        interval = QueryInterval(today=today)

        assert interval.today == today

    def test_accepts_a_start_and_end_range(self) -> None:
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)

        interval = QueryInterval(start=start, end=end)

        assert interval.today is None
        assert interval.start == start
        assert interval.end == end

    def test_raises_when_today_and_start_are_both_given(self) -> None:
        with pytest.raises(InvalidQueryInterval):
            QueryInterval(today=date(2024, 1, 1), start=date(2024, 1, 1))

    def test_raises_when_today_and_end_are_both_given(self) -> None:
        with pytest.raises(InvalidQueryInterval):
            QueryInterval(today=date(2024, 1, 1), end=date(2024, 1, 31))

    def test_raises_when_only_start_is_given(self) -> None:
        with pytest.raises(InvalidQueryInterval):
            QueryInterval(start=date(2024, 1, 1))

    def test_raises_when_only_end_is_given(self) -> None:
        with pytest.raises(InvalidQueryInterval):
            QueryInterval(end=date(2024, 1, 31))


class TestIntervalCaps:
    def test_a_full_year_is_accepted(self) -> None:
        # 366 days counting both ends covers any one-year view, leap or not.
        interval = QueryInterval(start=date(2024, 1, 1), end=date(2024, 12, 31))

        assert interval.start == date(2024, 1, 1)

    def test_longer_than_a_year_is_rejected(self) -> None:
        with pytest.raises(InvalidQueryInterval) as error:
            QueryInterval(start=date(2024, 1, 1), end=date(2025, 1, 1))

        assert error.value.status_code == 400
        assert "366" in error.value.detail

    def test_end_before_start_is_rejected(self) -> None:
        with pytest.raises(InvalidQueryInterval):
            QueryInterval(start=date(2024, 2, 1), end=date(2024, 1, 31))

    def test_a_single_day_is_accepted(self) -> None:
        QueryInterval(start=date(2024, 2, 1), end=date(2024, 2, 1))


class TestEnsureValidSpan:
    @pytest.mark.parametrize(
        ("days", "ok"), [(1, True), (31, True), (32, False)], ids=["1d", "31d", "32d"]
    )
    def test_counts_both_ends(self, days: int, ok: bool) -> None:
        start = date(2026, 3, 1)
        end = start + timedelta(days=days - 1)

        if ok:
            ensure_valid_span(start, end, max_days=31)
        else:
            with pytest.raises(InvalidQueryInterval):
                ensure_valid_span(start, end, max_days=31)
