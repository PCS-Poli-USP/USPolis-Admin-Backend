import pytest

from server.models.http.requests.allocation_request_models import (
    AllocationMapValue,
    InvalidAllocationMapValue,
)


class TestAllocationMapValue:
    def test_valid_input_passes(self) -> None:
        value = AllocationMapValue(schedule_id=1, classroom_ids=[1, 2])

        assert value.classroom_ids == [1, 2]

    def test_rejects_no_classrooms(self) -> None:
        with pytest.raises(InvalidAllocationMapValue):
            AllocationMapValue(schedule_id=1, classroom_ids=[])

    def test_rejects_a_non_positive_classroom_id(self) -> None:
        with pytest.raises(InvalidAllocationMapValue):
            AllocationMapValue(schedule_id=1, classroom_ids=[1, 0])

    def test_rejects_a_non_positive_schedule_id(self) -> None:
        with pytest.raises(InvalidAllocationMapValue):
            AllocationMapValue(schedule_id=0, classroom_ids=[1])
