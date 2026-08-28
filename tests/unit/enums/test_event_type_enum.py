import pytest

from server.utils.enums.event_type_enum import EventType, NoSuchEventType


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Palestra", EventType.TALK),
        ("Workshop", EventType.WORKSHOP),
        ("Processo Seletivo", EventType.SELECTION_PROCESS),
        ("Outro", EventType.OTHER),
    ],
)
def test_from_str_maps_known_labels(label: str, expected: EventType) -> None:
    assert EventType.from_str(label) == expected


def test_from_str_raises_for_unknown_label() -> None:
    with pytest.raises(NoSuchEventType):
        EventType.from_str("Invalido")


def test_values_returns_every_member() -> None:
    assert set(EventType.values()) == set(EventType)
