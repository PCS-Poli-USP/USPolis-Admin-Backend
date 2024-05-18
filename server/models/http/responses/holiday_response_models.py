from datetime import datetime
from pydantic import BaseModel

from server.models.database.holiday_db_model import Holiday
from server.utils.enums.holiday_type import HolidayType

class HolidayResponse(BaseModel):
    id: str
    category: str
    date: datetime
    type: HolidayType
    updated_at: datetime
    created_by: str

    @classmethod
    async def from_holiday(cls, holiday: Holiday) -> "HolidayResponse":
        await holiday.fetch_all_links()
        return cls(
            id=str(holiday.id),
            category=holiday.category.name, # type: ignore
            date=holiday.date,
            type=holiday.type,
            updated_at=holiday.updated_at,
            created_by=holiday.created_by.name,  # type: ignore
        )

    @classmethod
    async def from_holiday_list(cls, holidays: list[Holiday]) -> list["HolidayResponse"]:
        return [await cls.from_holiday(holiday) for holiday in holidays]
