from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.user_db_model import User
from server.models.http.requests.holiday_category_request_models import (
    HolidayCategoryRegister,
    HolidayCategoryUpdate,
)
from server.routes.restricted.holiday_category_routes import (
    HolidayCategoryAlreadyExists,
)


def make_holiday_category(name: str, user: User) -> HolidayCategory:
    return HolidayCategory(name=name, created_by=user) # type: ignore


def make_holiday_category_register(name: str) -> HolidayCategoryRegister:
    return HolidayCategoryRegister(name=name)


def make_holiday_category_update(name: str) -> HolidayCategoryUpdate:
    return HolidayCategoryUpdate(name=name)


async def add_holiday_category(name: str, user: User) -> str:
    if await HolidayCategory.check_name_exists(name):
        raise HolidayCategoryAlreadyExists(name)
    holiday_category = make_holiday_category(name, user)
    await holiday_category.create()
    return str(holiday_category.id)
