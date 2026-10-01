from server.utils.enums.allocation_enum import AllocationEnum


def test_values_returns_every_member() -> None:
    assert set(AllocationEnum.values()) == set(AllocationEnum)
