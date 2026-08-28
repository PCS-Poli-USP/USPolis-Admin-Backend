import pytest

from server.utils.enums.allocation_event_type_enum import AllocationEventType
from server.utils.enums.reservation_type import ReservationType


@pytest.mark.parametrize(
    ("reservation_type", "expected"),
    [
        (ReservationType.EXAM, AllocationEventType.EXAM),
        (ReservationType.EVENT, AllocationEventType.EVENT),
        (ReservationType.MEETING, AllocationEventType.MEETING),
    ],
)
def test_get_from_reservation_type_maps_known_types(
    reservation_type: ReservationType, expected: AllocationEventType
) -> None:
    assert AllocationEventType.get_from_reservation_type(reservation_type) == expected


def test_get_from_reservation_type_falls_back_to_event() -> None:
    assert (
        AllocationEventType.get_from_reservation_type("not-a-real-type")  # type: ignore[arg-type]
        == AllocationEventType.EVENT
    )


def test_values_returns_every_member() -> None:
    assert set(AllocationEventType.values()) == set(AllocationEventType)
