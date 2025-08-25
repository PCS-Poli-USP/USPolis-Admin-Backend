from datetime import datetime
from server.models.database.building_db_model import Building
from server.models.database.calendar_db_model import Calendar
from server.models.database.solicitation_db_model import (
    Solicitation,
)
from server.models.database.group_db_model import Group
from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.holiday_db_model import Holiday
from server.models.database.reservation_db_model import Reservation
from server.models.database.user_db_model import User
from server.models.dicts.base.user_base_dict import UserBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class UserModelDict(BaseModelDict, UserBaseDict, total=False):
    """TypedDict for User model.\n
    This TypedDict is used to define the structure of the User data.\n
    """

    email: str
    name: str
    updated_at: datetime
    last_visited: datetime
    created_by_id: int | None

    # Relationships
    created_by: User | None
    buildings: list[Building] | None
    holidays_categories: list[HolidayCategory]
    holidays: list[Holiday]
    calendars: list[Calendar]
    reservations: list[Reservation]
    solicitations: list[Solicitation]
    groups: list[Group]
