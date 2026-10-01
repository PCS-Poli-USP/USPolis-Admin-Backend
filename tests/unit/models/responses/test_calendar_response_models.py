from server.models.http.responses.calendar_response_models import CalendarResponse
from tests.utils.academic_test_utils import make_user
from tests.utils.time_test_utils import make_calendar, make_holiday_category


class TestCalendarResponse:
    def test_from_calendar(self) -> None:
        creator = make_user(name="Ana")
        category = make_holiday_category(creator=creator, name="Feriados")
        category.holidays = []
        calendar = make_calendar(
            creator=creator, name="Calendário 2025", year=2025, categories=[category]
        )

        data = CalendarResponse.from_calendar(calendar)

        assert data.id == calendar.id
        assert data.owner_id == creator.id
        assert data.name == "Calendário 2025"
        assert data.year == 2025
        assert data.created_by == "Ana"
        assert [c.id for c in data.categories] == [category.id]

    def test_from_calendar_list(self) -> None:
        creator = make_user()
        calendar1 = make_calendar(creator=creator)
        calendar2 = make_calendar(creator=creator)

        data = CalendarResponse.from_calendar_list([calendar1, calendar2])

        assert [d.id for d in data] == [calendar1.id, calendar2.id]
