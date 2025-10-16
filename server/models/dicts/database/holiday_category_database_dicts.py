from server.models.database.calendar_db_model import Calendar
from server.models.database.holiday_db_model import Holiday
from server.models.database.user_db_model import User
from server.models.dicts.base.holiday_category_base_dict import HolidayCategoryBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class HolidayCategoryModelDict(HolidayCategoryBaseDict, BaseModelDict, total=False):
    """TypedDict for HolidayCategory database model.\n
    This TypedDict is used to define the structure of the Holiday data.\n
    """

    created_by_id: int
    created_by: User

    holidays: list[Holiday]
    calendars: list[Calendar]
