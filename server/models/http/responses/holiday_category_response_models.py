from pydantic import BaseModel

from server.models.database.holiday_category_db_model import HolidayCategory


class HolidayCategoryResponse(BaseModel):
    id: str
    name: str
    created_by: str

    @classmethod
    async def from_holiday_category(cls, holiday_category: HolidayCategory) -> "HolidayCategoryResponse":
        await holiday_category.fetch_all_links()
        return cls(
            id=str(holiday_category.id),
            name=holiday_category.name,
            created_by=holiday_category.created_by.name,  # type: ignore
        )

    @classmethod
    async def from_holiday_category_list(cls, holidays_categories: list[HolidayCategory]) -> list["HolidayCategoryResponse"]:
        return [await cls.from_holiday_category(holiday_category) for holiday_category in holidays_categories]
