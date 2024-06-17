from datetime import datetime
from typing import Any, Dict


from pydantic import (
    BaseModel,
    model_validator,
)

from server.utils.day_time import DayTime
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class ScheduleBase(BaseModel):
    """Base for any schedule request of update or create"""

    start_date: datetime
    end_date: datetime
    recurrence: Recurrence
    skip_exceptions: bool
    all_day: bool
    allocated: bool | None


class ScheduleRegister(ScheduleBase):
    """Schedule register body"""

    week_day: WeekDay | None
    start_time: DayTime
    end_time: DayTime
    dates: list[datetime] | None
