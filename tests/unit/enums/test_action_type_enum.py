import pytest

from server.utils.enums.action_type_enum import ActionType, NoSuchActionType


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Alocar", ActionType.ALLOCATE),
        ("Desalocar", ActionType.DEALLOCATE),
    ],
)
def test_from_str_maps_known_labels(label: str, expected: ActionType) -> None:
    assert ActionType.from_str(label) == expected


def test_from_str_raises_for_unknown_label() -> None:
    with pytest.raises(NoSuchActionType):
        ActionType.from_str("Invalido")
