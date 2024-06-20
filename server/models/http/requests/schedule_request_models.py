from datetime import datetime, time
from typing import Any, Self

from fastapi import HTTPException, status
from pydantic import (
    BaseModel,
    model_validator,
)

from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class ScheduleBase(BaseModel):
    """Base for any schedule request of update or create"""

    start_date: datetime
    end_date: datetime
    recurrence: Recurrence = Recurrence.NONE
    skip_exceptions: bool = False
    all_day: bool = False
    allocated: bool | None = None


class ScheduleManyRegister(ScheduleBase):
    """Register Many Schedules"""

    week_days: list[WeekDay]
    start_times: list[time]
    end_times: list[time]

    @model_validator(mode="before")
    def check_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        week_days: list[WeekDay] = values.get("week_days", [])
        start_times: list[time] = values.get("start_times", [])
        end_times: list[time] = values.get("end_times", [])

        if not week_days or not start_times or not end_times:
            raise ValueError("Schedule info must not be empty")

        if len(week_days) != len(start_times) or len(week_days) != len(end_times):
            raise ValueError("Schedule allocation info must be with same size")

        return values


class ScheduleRegister(ScheduleBase):
    """Schedule register body"""

    class_id: int | None = None
    reservation_id: int | None = None
    classroom_id: int | None = None
    week_day: WeekDay | None = None
    start_time: time
    end_time: time
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
