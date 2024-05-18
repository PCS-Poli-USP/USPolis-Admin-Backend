from datetime import datetime
from fastapi import HTTPException, status
from beanie import Document, Link
from bson import ObjectId

from server.models.database.user_db_model import User
from server.models.database.holiday_category_db_model import HolidayCategory
from server.utils.enums.holiday_type import HolidayType

class Holiday(Document):
    category: Link[HolidayCategory]
    date: datetime
    type: HolidayType
    updated_at: datetime
    created_by: Link[User]

    class Settings:
        name = "holidays"

    @classmethod
    async def by_id(cls, id: str) -> "Holiday":
        holiday = await cls.get(id)
        if holiday is None:
            raise HolidayNotFound(id)
        return holiday

    @classmethod
    async def check_date_in_category_exists(cls, category_id: str, date: datetime) -> bool:
        """Check if a date already exists in a holiday category"""
        return await cls.find_one(
            {"category.$id": ObjectId(category_id), "date": date}
        ) is not None

    @classmethod
    async def check_date_is_valid(cls, category_id: str, holiday_id: str, date: datetime) -> bool:
        """Check if a holiday date is valid, i.e  not used by other holiday in same category"""
        holiday = await cls.find_one(
            {"category.$id": ObjectId(category_id), "date": date}
        )
        if holiday is None:
            return True
        return str(holiday.id) == holiday_id


class HolidayNotFound(HTTPException):
    def __init__(self, holiday_info: str) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"Holiday {holiday_info} not found")
