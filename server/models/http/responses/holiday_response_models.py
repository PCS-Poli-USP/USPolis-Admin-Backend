from datetime import datetime, date
from pydantic import BaseModel

from server.models.database.holiday_db_model import Holiday
from server.utils.must_be_int import must_be_int


class HolidayResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    category_id: int
    category: str
    date: date
    updated_at: datetime
    created_by: str

    @classmethod
    def from_holiday(cls, holiday: Holiday) -> "HolidayResponse":
        return cls(
            id=must_be_int(holiday.id),
            owner_id=must_be_int(holiday.created_by.id),
            name=holiday.name,
            category_id=must_be_int(holiday.category.id),
            category=holiday.category.name,
            date=holiday.date,
            updated_at=holiday.updated_at,
            created_by=holiday.created_by.name,
        )

    @classmethod
    def from_holiday_list(cls, holidays: list[Holiday]) -> list["HolidayResponse"]:
        return [cls.from_holiday(holiday) for holiday in holidays]
