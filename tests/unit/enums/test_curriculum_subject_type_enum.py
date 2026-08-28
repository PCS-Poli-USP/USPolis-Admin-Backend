import pytest

from server.utils.enums.curriculum_subject_type_enum import (
    CurriculumSubjectType,
    NoSuchCurriculumSubjectType,
)


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Semestral", CurriculumSubjectType.SEMESTRAL),
        ("Quadrimestral", CurriculumSubjectType.QUADRIMESTER),
    ],
)
def test_from_str_maps_known_labels(
    label: str, expected: CurriculumSubjectType
) -> None:
    assert CurriculumSubjectType.from_str(label) == expected


def test_from_str_raises_for_unknown_label() -> None:
    with pytest.raises(NoSuchCurriculumSubjectType):
        CurriculumSubjectType.from_str("Invalido")


def test_values_returns_every_member() -> None:
    assert set(CurriculumSubjectType.values()) == set(CurriculumSubjectType)
