from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.http.requests.holiday_category_request_models import (
    HolidayCategoryRegister,
    HolidayCategoryUpdate,
)
from server.routes.admin.holiday_category_routes import HolidayCategoryAlreadyExists


def make_holiday_category(category: str) -> HolidayCategory:
    return HolidayCategory(category=category)


def make_holiday_category_register(category: str) -> HolidayCategoryRegister:
    return HolidayCategoryRegister(category=category)


def make_holiday_category_update(category: str) -> HolidayCategoryUpdate:
    return HolidayCategoryUpdate(category=category)


async def add_holiday_category(category: str) -> str:
    if await HolidayCategory.check_category_exists(category):
        raise HolidayCategoryAlreadyExists(category)
    holiday_category = make_holiday_category(category)
    await holiday_category.create()
    return str(holiday_category.id)
