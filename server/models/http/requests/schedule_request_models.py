from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    model_validator,
)

from server.utils.day_time import DayTime
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class ScheduleBase(BaseModel):
    """Base for any schedule request of update or create"""

    calendar_ids: list[int]
    start_date: datetime
    end_date: datetime
    recurrence: Recurrence = Recurrence.NONE
    skip_exceptions: bool = False
    all_day: bool = False
    allocated: bool | None = None


class ScheduleManyRegister(ScheduleBase):
    """Register Many Schedules"""

    week_days: list[WeekDay]
    start_times: list[DayTime]
    end_times: list[DayTime]

    @model_validator(mode="before")
    def check_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        week_days: list[WeekDay] = values.get("week_days", [])
        start_times: list[DayTime] = values.get("start_times", [])
        end_times: list[DayTime] = values.get("end_times", [])

        if not week_days or not start_times or not end_times:
            raise ValueError("Schedule info must not be empty")

        if len(week_days) != len(start_times) or len(week_days) != len(end_times):
            raise ValueError("Schedule allocation info must be with same size")

        return values


class ScheduleRegister(ScheduleBase):
    """Register a single Schedule"""

    week_day: WeekDay
    start_time: DayTime
    end_time: DayTime
