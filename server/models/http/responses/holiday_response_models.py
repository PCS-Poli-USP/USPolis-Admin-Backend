from datetime import datetime
from pydantic import BaseModel

from server.models.database.holiday_db_model import Holiday


class HolidayResponse(BaseModel):
    id: int
    category: str
    date: datetime
    updated_at: datetime
    created_by: str

    @classmethod
    def from_holiday(cls, holiday: Holiday) -> "HolidayResponse":
        if holiday.id is None:
            raise ValueError(
                "Holiday ID is None, try refresh session if it is newly created"
            )
        return cls(
            id=holiday.id,
            category=holiday.category.name,  # type: ignore
            date=holiday.date,
            updated_at=holiday.updated_at,
            created_by=holiday.created_by.name,  # type: ignore
        )

    @classmethod
    def from_holiday_list(cls, holidays: list[Holiday]) -> list["HolidayResponse"]:
        return [cls.from_holiday(holiday) for holiday in holidays]
