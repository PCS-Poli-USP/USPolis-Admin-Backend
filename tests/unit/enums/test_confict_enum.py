from server.utils.enums.confict_enum import ConflictStatus, ConflictType


def test_conflict_type_values_returns_every_member() -> None:
    assert set(ConflictType.values()) == set(ConflictType)


def test_conflict_status_values_returns_every_member() -> None:
    assert set(ConflictStatus.values()) == set(ConflictStatus)
