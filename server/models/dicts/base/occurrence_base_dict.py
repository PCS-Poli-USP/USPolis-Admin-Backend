from datetime import date, time

from server.models.dicts.base.base_dict import BaseDict


class OccurrenceBaseDict(BaseDict, total=False):
    """Base dict for occurrence dictionaries (requests and database)"""

    start_time: time
    end_time: time
    date: date
