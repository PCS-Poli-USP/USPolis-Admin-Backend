from dataclasses import dataclass

from server.utils.common_utils import (
    compare_SQLModel_vectors_by_id,
    compare_SQLModel_vectors_by_objects,
)


@dataclass
class FakeRow:
    id: int | None
    label: str = "x"


class TestCompareSQLModelVectorsById:
    def test_true_when_ids_match_in_order(self) -> None:
        vec1 = [FakeRow(id=1), FakeRow(id=2)]
        vec2 = [FakeRow(id=1, label="different"), FakeRow(id=2, label="also different")]
        assert compare_SQLModel_vectors_by_id(vec1, vec2) is True

    def test_false_when_ids_differ(self) -> None:
        vec1 = [FakeRow(id=1), FakeRow(id=2)]
        vec2 = [FakeRow(id=1), FakeRow(id=3)]
        assert compare_SQLModel_vectors_by_id(vec1, vec2) is False

    def test_false_when_order_differs(self) -> None:
        vec1 = [FakeRow(id=1), FakeRow(id=2)]
        vec2 = [FakeRow(id=2), FakeRow(id=1)]
        assert compare_SQLModel_vectors_by_id(vec1, vec2) is False

    def test_false_when_lengths_differ(self) -> None:
        vec1 = [FakeRow(id=1)]
        vec2 = [FakeRow(id=1), FakeRow(id=2)]
        assert compare_SQLModel_vectors_by_id(vec1, vec2) is False

    def test_true_for_two_empty_vectors(self) -> None:
        assert compare_SQLModel_vectors_by_id([], []) is True


class TestCompareSQLModelVectorsByObjects:
    def test_true_when_objects_are_equal_in_order(self) -> None:
        vec1 = [FakeRow(id=1, label="a"), FakeRow(id=2, label="b")]
        vec2 = [FakeRow(id=1, label="a"), FakeRow(id=2, label="b")]
        assert compare_SQLModel_vectors_by_objects(vec1, vec2) is True

    def test_false_when_an_object_field_differs(self) -> None:
        vec1 = [FakeRow(id=1, label="a")]
        vec2 = [FakeRow(id=1, label="different")]
        assert compare_SQLModel_vectors_by_objects(vec1, vec2) is False

    def test_false_when_lengths_differ(self) -> None:
        vec1 = [FakeRow(id=1, label="a")]
        vec2 = [FakeRow(id=1, label="a"), FakeRow(id=2, label="b")]
        assert compare_SQLModel_vectors_by_objects(vec1, vec2) is False

    def test_true_for_two_empty_vectors(self) -> None:
        assert compare_SQLModel_vectors_by_objects([], []) is True
