from datetime import date, time
from server.models.dicts.base.base_dict import BaseDict
from server.utils.enums.recurrence import Recurrence


class ScheduleBaseDict(BaseDict, total=False):
    """
    Base dict for schedule dictionaries (requests and database)
    """

    start_date: date
    end_date: date
    start_time: time
    end_time: time
    recurrence: Recurrence
    all_day: bool
    allocated: bool
