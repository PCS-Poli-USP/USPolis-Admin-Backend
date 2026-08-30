from datetime import datetime

from server.models.database.schedule_db_model import Schedule
from server.models.database.user_schedule_db_model import UserSchedule
from server.models.dicts.base.user_schedule_entry_base_dict import (
    UserScheduleEntryBaseDict,
)
from server.models.dicts.database.base_database_dicts import BaseModelDict


class UserScheduleEntryModelDict(UserScheduleEntryBaseDict, BaseModelDict, total=False):
    """TypedDict for UserScheduleEntry database model.\n
    Inherits BaseModelDict's `id` key for consistency with every other model
    dict even though the model itself has no `id` column (its primary key is
    the composite (user_schedule_id, schedule_id)) - the key is simply never
    populated for this model."""

    user_schedule_id: int
    schedule_id: int
    user_schedule: UserSchedule
    schedule: Schedule
    created_at: datetime
    updated_at: datetime
