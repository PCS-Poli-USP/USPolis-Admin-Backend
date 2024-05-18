from beanie import Document, Link
from fastapi import HTTPException, status
from typing import Self

from server.models.database.user_db_model import User


class HolidayCategory(Document):
    name: str
    created_by: Link[User]

    class Settings:
        name = "holiday_categories"

    @classmethod
    async def by_id(cls, id: str) -> Self:
        category = await cls.get(id)
        if category is None:
            raise HolidayCategoryNotFound(id)
        return category

    @classmethod
    async def by_name(cls, name: str) -> Self:
        holiday_category = await cls.find_one(HolidayCategory.name == name)
        if holiday_category is None:
            raise HolidayCategoryNotFound(name)
        return holiday_category

    @classmethod
    async def check_name_exists(cls, name: str) -> bool:
        """Check if exists a Holiday Category with this name"""
        return await cls.find_one(HolidayCategory.name == name) is not None

    @classmethod
    async def check_category_is_valid(cls, holiday_category_id: str, name: str) -> bool:
        """Check if this category name is not used in other holiday category"""
        current = await cls.find_one(HolidayCategory.name == name)
        if current is None:
            return True
        return str(current.id) == holiday_category_id

class HolidayCategoryNotFound(HTTPException):
    def __init__(self, holiday_category_info: str) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"Holiday Category {holiday_category_info} not found")
