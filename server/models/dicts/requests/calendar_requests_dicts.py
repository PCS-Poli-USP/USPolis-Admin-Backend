from server.models.dicts.base.calendar_base_dict import CalendarBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class CalendarRegisterDict(CalendarBaseDict, BaseRequestDict, total=False):
    categories_ids: list[int] | None


class CalendarUpdateDict(CalendarRegisterDict, total=False):
    pass
