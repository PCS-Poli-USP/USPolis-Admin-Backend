from datetime import time

import pytz

from server.utils.time_utils import TimeUtils


def test_time_from_string_parses_hh_mm() -> None:
    result = TimeUtils.time_from_string("14:30")
    assert result.hour == 14
    assert result.minute == 30


def test_time_from_string_parses_hh_mm_ss() -> None:
    result = TimeUtils.time_from_string("08:05:30")
    assert result == time(8, 5, 30, tzinfo=pytz.timezone("America/Sao_Paulo"))


def test_time_from_string_attaches_sao_paulo_timezone() -> None:
    result = TimeUtils.time_from_string("09:00")
    assert result.tzinfo == pytz.timezone("America/Sao_Paulo")
