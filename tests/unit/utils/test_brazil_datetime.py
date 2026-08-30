from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from server.utils.brazil_datetime import BrazilDatetime


def test_brazil_tz_returns_sao_paulo_timezone() -> None:
    assert BrazilDatetime.brazil_tz() == ZoneInfo("America/Sao_Paulo")


def test_now_utc_returns_a_naive_datetime() -> None:
    now = BrazilDatetime.now_utc()
    assert now.tzinfo is None


def test_now_utc_matches_the_current_time_in_sao_paulo() -> None:
    now = BrazilDatetime.now_utc()
    reference = datetime.now(tz=BrazilDatetime.brazil_tz()).replace(tzinfo=None)
    assert abs((now - reference).total_seconds()) < 5


def test_format_brazil_formats_as_day_month_year() -> None:
    dt = BrazilDatetime(2025, 3, 7, 10, 30)
    assert dt.format_brazil() == "07/03/2025"


class TestCurrentSemester:
    def test_returns_first_semester_when_month_is_in_first_half(self) -> None:
        with patch(
            "server.utils.brazil_datetime.BrazilDatetime.now_utc",
            return_value=BrazilDatetime(2025, 3, 15),
        ):
            start, end = BrazilDatetime.current_semester()
        assert start == BrazilDatetime(2025, 1, 1)
        assert end == BrazilDatetime(2025, 6, 30)

    def test_returns_first_semester_boundary_month_june(self) -> None:
        with patch(
            "server.utils.brazil_datetime.BrazilDatetime.now_utc",
            return_value=BrazilDatetime(2025, 6, 30),
        ):
            start, end = BrazilDatetime.current_semester()
        assert start == BrazilDatetime(2025, 1, 1)
        assert end == BrazilDatetime(2025, 6, 30)

    def test_returns_second_semester_when_month_is_in_second_half(self) -> None:
        with patch(
            "server.utils.brazil_datetime.BrazilDatetime.now_utc",
            return_value=BrazilDatetime(2025, 9, 1),
        ):
            start, end = BrazilDatetime.current_semester()
        assert start == BrazilDatetime(2025, 7, 1)
        assert end == BrazilDatetime(2026, 1, 1)

    def test_returns_second_semester_boundary_month_july(self) -> None:
        with patch(
            "server.utils.brazil_datetime.BrazilDatetime.now_utc",
            return_value=BrazilDatetime(2025, 7, 1),
        ):
            start, end = BrazilDatetime.current_semester()
        assert start == BrazilDatetime(2025, 7, 1)
        assert end == BrazilDatetime(2026, 1, 1)
