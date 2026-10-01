import pytest

from server.utils.enums.curriculum_subject_category_enum import (
    CurriculumSubjectCategory,
    NoSuchCurriculumSubjectCategory,
)


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Obrigatória", CurriculumSubjectCategory.MANDATORY),
        ("Optativa Livre", CurriculumSubjectCategory.FREE_ELECTIVE),
        ("Optativa Eletiva", CurriculumSubjectCategory.TRACK_ELECTIVE),
    ],
)
def test_from_str_maps_known_labels(
    label: str, expected: CurriculumSubjectCategory
) -> None:
    assert CurriculumSubjectCategory.from_str(label) == expected


def test_from_str_raises_for_unknown_label() -> None:
    with pytest.raises(NoSuchCurriculumSubjectCategory):
        CurriculumSubjectCategory.from_str("Invalido")


def test_values_returns_every_member() -> None:
    assert set(CurriculumSubjectCategory.values()) == set(CurriculumSubjectCategory)
