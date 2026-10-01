from server.models.http.responses.holiday_category_response_models import (
    HolidayCategoryResponse,
)
from tests.utils.academic_test_utils import make_user
from tests.utils.time_test_utils import make_holiday, make_holiday_category


class TestHolidayCategoryResponse:
    def test_from_holiday_category(self) -> None:
        creator = make_user(name="Ana")
        category = make_holiday_category(creator=creator, name="Feriados", year=2025)
        holiday = make_holiday(creator=creator, category=category)
        category.holidays = [holiday]

        data = HolidayCategoryResponse.from_holiday_category(category)

        assert data.id == category.id
        assert data.owner_id == creator.id
        assert data.name == "Feriados"
        assert data.year == 2025
        assert data.created_by == "Ana"
        assert [h.id for h in data.holidays] == [holiday.id]

    def test_from_holiday_category_list(self) -> None:
        creator = make_user()
        category1 = make_holiday_category(creator=creator)
        category1.holidays = []
        category2 = make_holiday_category(creator=creator)
        category2.holidays = []

        data = HolidayCategoryResponse.from_holiday_category_list(
            [category1, category2]
        )

        assert [d.id for d in data] == [category1.id, category2.id]
