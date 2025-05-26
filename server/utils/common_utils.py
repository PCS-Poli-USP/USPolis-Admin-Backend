from typing import Protocol, TypeVar
from collections.abc import Sequence


class GenericTable(Protocol):
    id: int | None


T = TypeVar("T", bound=GenericTable)


def compare_SQLModel_vectors_by_id(vec1: Sequence[T], vec2: Sequence[T]) -> bool:
    """Compare if two vectors of sqlmodel objects are equals by objects id"""
    if len(vec1) != len(vec2):
        return False

    ids1 = [obj.id for obj in vec1]
    ids2 = [obj.id for obj in vec2]

    return ids1 == ids2


def compare_SQLModel_vectors_by_objects(vec1: Sequence[T], vec2: Sequence[T]) -> bool:
    if len(vec1) != len(vec2):
        return False

    for obj1, obj2 in zip(vec1, vec2):
        if obj1 != obj2:
            return False

    return True
