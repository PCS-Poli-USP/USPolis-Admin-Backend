from beanie import Document
from fastapi import HTTPException, status
from typing import Self


class HolidayCategory(Document):
    category: str

    class Settings:
        name = "holiday_categories"

    @classmethod
    async def by_id(cls, id: str) -> Self:
        category = await cls.get(id)
        if category is None:
            raise HolidayCategoryNotFound(id)
        return category

    @classmethod
    async def by_category(cls, category: str) -> Self:
        holiday_category = await cls.find_one(HolidayCategory.category == category)
        if holiday_category is None:
            raise HolidayCategoryNotFound(category)
        return holiday_category

    @classmethod
    async def check_category_exists(cls, category: str) -> bool:
        """Check if exists a holiday category with this category"""
        return await cls.find_one(HolidayCategory.category == category) is not None

    @classmethod
    async def check_category_is_valid(cls, holiday_category_id: str, category: str) -> bool:
        """Check if this category is not used in other holiday category"""
        current = await cls.find_one(HolidayCategory.category == category)
        if current is None:
            return True
        return str(current.id) == holiday_category_id

class HolidayCategoryNotFound(HTTPException):
    def __init__(self, holiday_category_info: str) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"Holiday Category {holiday_category_info} not found")
