from datetime import date

from server.models.http.responses.holiday_response_models import HolidayResponse
from tests.utils.academic_test_utils import make_user
from tests.utils.time_test_utils import make_holiday, make_holiday_category


class TestHolidayResponse:
    def test_from_holiday(self) -> None:
        creator = make_user(name="Ana")
        category = make_holiday_category(creator=creator, name="Feriados Nacionais")
        holiday = make_holiday(
            creator=creator,
            category=category,
            name="Independência",
            holiday_date=date(2025, 9, 7),
        )

        data = HolidayResponse.from_holiday(holiday)

        assert data.id == holiday.id
        assert data.owner_id == creator.id
        assert data.name == "Independência"
        assert data.category_id == category.id
        assert data.category == "Feriados Nacionais"
        assert data.date == date(2025, 9, 7)
        assert data.created_by == "Ana"

    def test_from_holiday_list(self) -> None:
        creator = make_user()
        category = make_holiday_category(creator=creator)
        holiday1 = make_holiday(creator=creator, category=category)
        holiday2 = make_holiday(creator=creator, category=category)

        data = HolidayResponse.from_holiday_list([holiday1, holiday2])

        assert [d.id for d in data] == [holiday1.id, holiday2.id]
