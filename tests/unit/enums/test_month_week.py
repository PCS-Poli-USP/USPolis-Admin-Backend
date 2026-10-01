from server.utils.enums.month_week import MonthWeek


def test_values_returns_every_member() -> None:
    assert set(MonthWeek.values()) == set(MonthWeek)


def test_last_is_represented_as_negative_one() -> None:
    assert MonthWeek.LAST.value == -1
