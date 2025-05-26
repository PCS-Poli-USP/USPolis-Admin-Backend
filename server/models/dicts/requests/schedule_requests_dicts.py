from datetime import date
from server.models.dicts.base.schedule_base_dict import ScheduleBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.week_day import WeekDay


class ScheduleRegisterDict(ScheduleBaseDict, BaseRequestDict, total=False):
    """TypedDict for Schedule request model.\n
    This TypedDict is used to define the structure of the Schedule input data.\n
    """

    class_id: int | None
    reservation_id: int | None
    classroom_id: int | None
    week_day: WeekDay | None
    month_week: MonthWeek | None
    dates: list[date] | None


class ScheduleUpdateDict(ScheduleRegisterDict, total=False):
    pass


class ScheduleUpdateOccurrenceDict(BaseRequestDict, total=False):
    dates: list[date]
