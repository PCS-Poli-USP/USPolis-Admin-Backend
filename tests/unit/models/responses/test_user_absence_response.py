from datetime import date

from server.models.http.responses.user_absence_response import UserAbsenceResponse
from tests.utils.user_schedule_test_utils import make_user_absence


class TestUserAbsenceResponse:
    def test_from_absence(self) -> None:
        absence = make_user_absence(
            user_schedule_id=5,
            schedule_id=7,
            absence_date=date(2025, 3, 10),
            note="Viagem",
        )

        data = UserAbsenceResponse.from_absence(absence)

        assert data.id == absence.id
        assert data.user_schedule_id == 5
        assert data.schedule_id == 7
        assert data.absence_date == date(2025, 3, 10)
        assert data.note == "Viagem"

    def test_from_absences(self) -> None:
        absence1 = make_user_absence(user_schedule_id=1, schedule_id=1)
        absence2 = make_user_absence(user_schedule_id=1, schedule_id=1)

        data = UserAbsenceResponse.from_absences([absence1, absence2])

        assert [d.id for d in data] == [absence1.id, absence2.id]
