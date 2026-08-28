import pytest

from server.utils.enums.subject_type import NoSuchSubjectType, SubjectType


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Semestral", SubjectType.BIANNUAL),
        ("Quadrimestral", SubjectType.FOUR_MONTHLY),
        ("Pós-graduação", SubjectType.POSTGRADUATE),
        ("Outro", SubjectType.OTHER),
    ],
)
def test_from_str_maps_known_labels(label: str, expected: SubjectType) -> None:
    assert SubjectType.from_str(label) == expected


def test_from_str_raises_for_unknown_label() -> None:
    with pytest.raises(NoSuchSubjectType):
        SubjectType.from_str("Invalido")


def test_values_returns_every_member() -> None:
    assert set(SubjectType.values()) == set(SubjectType)
