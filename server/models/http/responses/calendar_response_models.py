from pydantic import BaseModel

from server.models.database.calendar_db_model import Calendar
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.holiday_category_response_models import (
    HolidayCategoryResponse,
)


class CalendarResponse(BaseModel):
    id: int
    name: str
    categories: list[HolidayCategoryResponse]
    created_by: str

    @classmethod
    def from_calendar(cls, calendar: Calendar) -> "CalendarResponse":
        if calendar.id is None:
            raise UnfetchDataError("Calendar", "ID")
        return cls(
            id=calendar.id,
            name=calendar.name,
            categories=HolidayCategoryResponse.from_holiday_category_list(
                calendar.categories
            ),
            created_by=calendar.created_by.name,
        )

    @classmethod
    def from_calendar_list(cls, calendars: list[Calendar]) -> list["CalendarResponse"]:
        return [cls.from_calendar(calendar) for calendar in calendars]
