from server.models.dicts.base.base_dict import BaseDict


class UserScheduleEntryBaseDict(BaseDict, total=False):
    """Base dict for user schedule entry dictionaries (requests and database)"""

    absence_count: int
