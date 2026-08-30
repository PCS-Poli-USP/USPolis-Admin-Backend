from datetime import datetime

from server.models.database.user_db_model import User
from server.models.database.user_schedule_entry_db_model import UserScheduleEntry
from server.models.dicts.base.user_schedule_base_dict import UserScheduleBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class UserScheduleModelDict(UserScheduleBaseDict, BaseModelDict, total=False):
    """User schedule model dictionary for the database."""

    user_id: int
    user: User
    entries: list[UserScheduleEntry]
    created_at: datetime
    updated_at: datetime
