from server.models.http.responses.user_schedule_response import UserScheduleResponse
from tests.utils.academic_test_utils import make_user
from tests.utils.time_test_utils import make_schedule
from tests.utils.user_schedule_test_utils import make_user_schedule, make_user_schedule_entry


class TestUserScheduleResponse:
    def test_from_user_schedule_with_entries(self) -> None:
        user = make_user()
        user_schedule = make_user_schedule(user=user)
        schedule = make_schedule()
        entry = make_user_schedule_entry(user_schedule=user_schedule, schedule=schedule)
        user_schedule.entries = [entry]

        data = UserScheduleResponse.from_user_schedule(user, user_schedule)

        assert data.id == user_schedule.id
        assert data.user_id == user.id
        assert data.start_date == user_schedule.start_date
        assert [e.schedule_id for e in data.entries] == [schedule.id]

    def test_from_user_schedule_with_no_schedule_uses_current_schedule_id(self) -> None:
        user = make_user()
        user.current_schedule_id = 42

        data = UserScheduleResponse.from_user_schedule(user, None)

        assert data.id == 42
        assert data.user_id == user.id
        assert data.entries == []
        assert data.start_date is None

    def test_from_user_schedule_with_no_schedule_and_no_current_schedule_id(
        self,
    ) -> None:
        user = make_user()
        user.current_schedule_id = None

        data = UserScheduleResponse.from_user_schedule(user, None)

        assert data.id is None
