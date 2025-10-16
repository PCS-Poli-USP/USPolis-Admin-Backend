from datetime import datetime
from server.models.dicts.base.holiday_base_dict import HolidayBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class HolidayRegisterDict(HolidayBaseDict, BaseRequestDict, total=False):
    date: datetime


class HolidayUpdateDict(HolidayRegisterDict, total=False):
    pass


class HolidayManyRegisterDict(HolidayBaseDict, BaseRequestDict, total=False):
    dates: list[datetime]
