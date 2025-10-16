from datetime import datetime, date as datetime_date
from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.user_db_model import User
from server.models.dicts.base.holiday_base_dict import HolidayBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class HolidayModelDict(HolidayBaseDict, BaseModelDict, total=False):
    """TypedDict for Holiday database model.\n
    This TypedDict is used to define the structure of the Holiday data.\n
    """

    date: datetime_date
    updated_at: datetime

    category: HolidayCategory

    created_by_id: int
    created_by: User
