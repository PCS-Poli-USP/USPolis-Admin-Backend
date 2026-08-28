import pytest

from server.utils.enums.class_type import ClassType, NoSuchClassType


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Prática", ClassType.PRACTIC),
        ("Teórica", ClassType.THEORIC),
        ("Teórica Vinculada", ClassType.VINCULATED_THEORIC),
        ("Prática Vinculada", ClassType.VINCULATED_PRACTIC),
    ],
)
def test_from_str_maps_known_labels(label: str, expected: ClassType) -> None:
    assert ClassType.from_str(label) == expected


def test_from_str_raises_for_unknown_label() -> None:
    with pytest.raises(NoSuchClassType):
        ClassType.from_str("Invalido")


def test_values_returns_every_member() -> None:
    assert set(ClassType.values()) == set(ClassType)
