from datetime import date

import pytest

from server.deps.interval_dep import InvalidQueryInterval, QueryInterval


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
