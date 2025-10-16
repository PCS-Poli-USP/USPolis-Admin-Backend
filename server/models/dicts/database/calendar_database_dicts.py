from server.models.database.class_db_model import Class
from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.user_db_model import User
from server.models.dicts.base.calendar_base_dict import CalendarBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class CalendarModelDict(CalendarBaseDict, BaseModelDict, total=False):
    """TypedDict for Calendar database model.\n
    This TypedDict is used to define the structure of the Calendar data.\n
    """

    created_by_id: int
    created_by: User

    categories: list[HolidayCategory]
    classes: list[Class]
