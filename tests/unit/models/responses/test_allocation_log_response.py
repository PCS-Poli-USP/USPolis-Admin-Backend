from server.models.http.responses.allocation_log_response import AllocationLogResponse
from server.utils.enums.action_type_enum import ActionType
from tests.utils.academic_test_utils import make_allocation_log
from tests.utils.time_test_utils import make_schedule


class TestAllocationLogResponse:
    def test_from_allocation_log(self) -> None:
        schedule = make_schedule()
        log = make_allocation_log(schedule=schedule, action=ActionType.DEALLOCATE)

        data = AllocationLogResponse.from_allocation_log(log)

        assert data.id == log.id
        assert data.action == ActionType.DEALLOCATE
        assert data.user_email == log.user_email
        assert data.schedule_id == schedule.id

    def test_from_allocation_logs(self) -> None:
        schedule = make_schedule()
        log1 = make_allocation_log(schedule=schedule)
        log2 = make_allocation_log(schedule=schedule)

        data = AllocationLogResponse.from_allocation_logs([log1, log2])

        assert [d.id for d in data] == [log1.id, log2.id]
