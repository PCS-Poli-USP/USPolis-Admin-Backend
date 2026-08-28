import pytest

from server.utils.enums.course_period_type_enum import (
    CoursePeriodType,
    NoSuchCoursePeriodType,
)


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Matutino", CoursePeriodType.MORNING),
        ("Vespertino", CoursePeriodType.AFTERNOON),
        ("Noturno", CoursePeriodType.EVENING),
        ("Integral", CoursePeriodType.INTEGRAL),
    ],
)
def test_from_str_maps_known_labels(label: str, expected: CoursePeriodType) -> None:
    assert CoursePeriodType.from_str(label) == expected


def test_from_str_raises_for_unknown_label() -> None:
    with pytest.raises(NoSuchCoursePeriodType):
        CoursePeriodType.from_str("Invalido")


def test_values_returns_every_member() -> None:
    assert set(CoursePeriodType.values()) == set(CoursePeriodType)
