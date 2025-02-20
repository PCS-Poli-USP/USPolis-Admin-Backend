from pydantic import BaseModel

from server.models.database.calendar_db_model import Calendar
from server.models.http.responses.holiday_category_response_models import (
    HolidayCategoryResponse,
)
from server.utils.must_be_int import must_be_int


class CalendarResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    categories: list[HolidayCategoryResponse]
    created_by: str

    @classmethod
    def from_calendar(cls, calendar: Calendar) -> "CalendarResponse":
        return cls(
            id=must_be_int(calendar.id),
            owner_id=must_be_int(calendar.created_by.id),
            name=calendar.name,
            categories=HolidayCategoryResponse.from_holiday_category_list(
                calendar.categories
            ),
            created_by=calendar.created_by.name,
        )

    @classmethod
    def from_calendar_list(cls, calendars: list[Calendar]) -> list["CalendarResponse"]:
        return [cls.from_calendar(calendar) for calendar in calendars]
