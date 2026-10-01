from datetime import date

from server.models.dicts.base.base_dict import BaseDict


class UserScheduleBaseDict(BaseDict, total=False):
    """Base dict for user schedule dictionaries (requests and database)"""

    start_date: date
    end_date: date
