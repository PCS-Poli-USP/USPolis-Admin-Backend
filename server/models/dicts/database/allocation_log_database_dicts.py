from datetime import datetime

from server.models.database.schedule_db_model import Schedule
from server.models.dicts.base.allocation_log_base_dict import AllocationLogBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class AllocationLogModelDict(AllocationLogBaseDict, BaseModelDict, total=False):
    """Allocation log model dictionary for the database."""

    modified_at: datetime
    schedule_id: int
    schedule: Schedule
