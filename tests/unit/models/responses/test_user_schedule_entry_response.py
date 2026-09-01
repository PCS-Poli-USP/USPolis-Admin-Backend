from server.models.http.responses.user_schedule_entry_response import (
    UserScheduleEntryResponse,
)
from server.utils.must_be_int import must_be_int
from tests.utils.academic_test_utils import make_user
from tests.utils.time_test_utils import make_schedule
from tests.utils.user_schedule_test_utils import (
    make_user_absence,
    make_user_schedule,
    make_user_schedule_entry,
)


class TestUserScheduleEntryResponse:
    def test_from_user_schedule_entry(self) -> None:
        user = make_user()
        user_schedule = make_user_schedule(user=user)
        schedule = make_schedule()
        entry = make_user_schedule_entry(user_schedule=user_schedule, schedule=schedule)
        absence = make_user_absence(
            user_schedule_id=must_be_int(user_schedule.id),
            schedule_id=must_be_int(schedule.id),
        )
        entry.absences = [absence]

        data = UserScheduleEntryResponse.from_user_schedule_entry(entry)

        assert data.user_schedule_id == user_schedule.id
        assert data.schedule_id == schedule.id
        assert data.schedule_data.id == schedule.id
        assert [a.id for a in data.absences] == [absence.id]

    def test_from_user_schedule_entries(self) -> None:
        user = make_user()
        user_schedule = make_user_schedule(user=user)
        schedule1 = make_schedule()
        schedule2 = make_schedule()
        entry1 = make_user_schedule_entry(user_schedule=user_schedule, schedule=schedule1)
        entry2 = make_user_schedule_entry(user_schedule=user_schedule, schedule=schedule2)

        data = UserScheduleEntryResponse.from_user_schedule_entries([entry1, entry2])

        assert [d.schedule_id for d in data] == [schedule1.id, schedule2.id]
