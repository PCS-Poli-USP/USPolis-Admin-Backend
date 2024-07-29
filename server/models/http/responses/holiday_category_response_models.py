from pydantic import BaseModel

from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.http.responses.holiday_response_models import HolidayResponse
from server.utils.must_be_int import must_be_int


class HolidayCategoryResponse(BaseModel):
    id: int
    name: str
    created_by: str
    holidays: list[HolidayResponse]

    @classmethod
    def from_holiday_category(
        cls, holiday_category: HolidayCategory
    ) -> "HolidayCategoryResponse":
        return cls(
            id=must_be_int(holiday_category.id),
            name=holiday_category.name,
            created_by=holiday_category.created_by.name,
            holidays=HolidayResponse.from_holiday_list(holiday_category.holidays),
        )

    @classmethod
    def from_holiday_category_list(
        cls, holidays_categories: list[HolidayCategory]
    ) -> list["HolidayCategoryResponse"]:
        return [
            cls.from_holiday_category(holiday_category)
            for holiday_category in holidays_categories
        ]
