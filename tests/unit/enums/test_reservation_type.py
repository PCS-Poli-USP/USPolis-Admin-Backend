import pytest

from server.utils.enums.reservation_type import (
    NoSuchReservationType,
    ReservationType,
)


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Prova", ReservationType.EXAM),
        ("Reunião", ReservationType.MEETING),
        ("Evento", ReservationType.EVENT),
    ],
)
def test_from_str_maps_known_labels(label: str, expected: ReservationType) -> None:
    assert ReservationType.from_str(label) == expected


def test_from_str_raises_for_unknown_label() -> None:
    with pytest.raises(NoSuchReservationType):
        ReservationType.from_str("Invalido")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (ReservationType.EXAM, "Prova"),
        (ReservationType.MEETING, "Reunião"),
        (ReservationType.EVENT, "Evento"),
    ],
)
def test_to_str_is_the_inverse_of_from_str(
    value: ReservationType, expected: str
) -> None:
    assert ReservationType.to_str(value) == expected
    assert ReservationType.from_str(expected) == value


def test_get_color_returns_a_distinct_color_per_type() -> None:
    colors = {ReservationType.get_color(v) for v in ReservationType.values()}
    assert len(colors) == len(ReservationType.values())


def test_values_returns_every_member() -> None:
    assert set(ReservationType.values()) == set(ReservationType)
