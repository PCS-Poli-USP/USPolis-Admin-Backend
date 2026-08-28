import pytest

from server.utils.enums.week_day import NoSuchWeekDay, WeekDay


@pytest.mark.parametrize(
    ("short", "expected"),
    [
        ("seg", WeekDay.MONDAY),
        ("ter", WeekDay.TUESDAY),
        ("qua", WeekDay.WEDNESDAY),
        ("qui", WeekDay.THURSDAY),
        ("sex", WeekDay.FRIDAY),
        ("sab", WeekDay.SATURDAY),
        ("dom", WeekDay.SUNDAY),
    ],
)
def test_from_str_maps_known_short_labels(short: str, expected: WeekDay) -> None:
    assert WeekDay.from_str(short) == expected
    assert WeekDay.from_str(short.upper()) == expected


def test_from_str_raises_for_unknown_label() -> None:
    with pytest.raises(NoSuchWeekDay):
        WeekDay.from_str("invalido")


@pytest.mark.parametrize(
    ("long", "expected"),
    [
        ("segunda", WeekDay.MONDAY),
        ("terça", WeekDay.TUESDAY),
        ("quarta", WeekDay.WEDNESDAY),
        ("quinta", WeekDay.THURSDAY),
        ("sexta", WeekDay.FRIDAY),
        ("sábado", WeekDay.SATURDAY),
        ("domingo", WeekDay.SUNDAY),
    ],
)
def test_from_long_str_maps_known_long_labels(long: str, expected: WeekDay) -> None:
    assert WeekDay.from_long_str(long) == expected
    assert WeekDay.from_long_str(long.upper()) == expected


def test_from_long_str_raises_for_unknown_label() -> None:
    with pytest.raises(NoSuchWeekDay):
        WeekDay.from_long_str("invalido")


def test_to_str_is_the_inverse_of_from_str() -> None:
    for day in WeekDay.values():
        short = WeekDay.to_str(day.value)
        assert WeekDay.from_str(short) == day


def test_to_int_returns_the_underlying_value() -> None:
    assert WeekDay.to_int(WeekDay.MONDAY) == 0
    assert WeekDay.to_int(WeekDay.SUNDAY) == 6


def test_to_rrule_maps_to_ical_two_letter_codes() -> None:
    assert WeekDay.to_rrule(WeekDay.MONDAY.value) == "MO"
    assert WeekDay.to_rrule(WeekDay.SUNDAY.value) == "SU"


def test_values_returns_every_member() -> None:
    assert set(WeekDay.values()) == set(WeekDay)


def test_workdays_excludes_the_weekend() -> None:
    workdays = WeekDay.workdays()
    assert WeekDay.SATURDAY not in workdays
    assert WeekDay.SUNDAY not in workdays
    assert len(workdays) == 5
