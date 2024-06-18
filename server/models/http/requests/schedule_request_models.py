from datetime import datetime
from typing import Self


from fastapi import HTTPException, status
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
    allocated: bool | None = None


class ScheduleRegister(ScheduleBase):
    """Schedule register body"""

    class_id: int | None = None
    reservation_id: int | None = None
    classroom_id: int | None = None
    week_day: WeekDay | None = None
    start_time: DayTime
    end_time: DayTime
    dates: list[datetime] | None = None

    @model_validator(mode="after")
    def check_class_id_and_reservation_id(self) -> Self:
        class_id = self.class_id
        reservation_id = self.class_id
        week_day = self.week_day
        recurrence = self.recurrence
        dates = self.dates

        # if class_id is None and reservation_id is None:
        #     raise ValueError("Class Id and Reservation Id cannot be both empty")

        if class_id is not None and reservation_id is not None:
            raise ScheduleInvalidData("Class Id", "Reservation Id")

        if week_day is None:
            if recurrence != Recurrence.CUSTOM and recurrence != Recurrence.DAILY:
                raise ScheduleInvalidData("Week Day", "Recurrence")
        if dates is not None:
            if recurrence != Recurrence.CUSTOM:
                raise ScheduleInvalidData("Dates", "Recurrence")

        return self


class ScheduleUpdate(ScheduleRegister):
    pass


class ScheduleInvalidData(HTTPException):
    def __init__(self, schedule_info: str, data_info: str) -> None:
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            f"Schedule with {schedule_info} has invalid {data_info} value",
        )
