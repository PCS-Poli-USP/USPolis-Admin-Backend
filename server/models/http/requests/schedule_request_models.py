from datetime import date, time
from typing import Self

from fastapi import HTTPException, status
from pydantic import (
    BaseModel,
    model_validator,
)

from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class ScheduleBase(BaseModel):
    """Base for any schedule request of update or create"""

    start_date: date
    end_date: date
    start_time: time
    end_time: time
    recurrence: Recurrence
    all_day: bool = False
    allocated: bool = False


class ScheduleRegister(ScheduleBase):
    """Schedule register body"""

    class_id: int | None = None
    reservation_id: int | None = None
    classroom_id: int | None = None
    week_day: WeekDay | None = None
    month_week: MonthWeek | None = None
    dates: list[date] | None = None

    @model_validator(mode="after")
    def check_class_body(self) -> Self:
        class_id = self.class_id
        reservation_id = self.class_id
        week_day = self.week_day
        month_week = self.month_week
        recurrence = self.recurrence
        dates = self.dates
        allocated = self.allocated
        classroom_id = self.classroom_id
        reservation_id = self.reservation_id

        if class_id is not None and reservation_id is not None:
            raise ScheduleConflictedData("Class Id", "Reservation Id")

        if week_day is None:
            if recurrence != Recurrence.CUSTOM and recurrence != Recurrence.DAILY:
                raise ScheduleInvalidData("Week Day", "Recurrence")

        if month_week is not None:
            if recurrence != Recurrence.MONTHLY:
                raise ScheduleInvalidData("Month Week", "Recurrence")

        if dates is not None:
            if recurrence != Recurrence.CUSTOM:
                raise ScheduleInvalidData("Dates", "Recurrence")

        if allocated:
            if classroom_id is None and reservation_id is None:
                raise ScheduleInvalidData(
                    "Allocated", "Classroom ID and Reservation ID"
                )

        return self


class ScheduleManyRegister(BaseModel):
    """Schedule register body for many schedules"""

    inputs: list[ScheduleRegister]


class ScheduleUpdate(ScheduleRegister):
    pass


class ScheduleUpdateOccurrences(BaseModel):
    dates: list[date]


class ScheduleInvalidData(HTTPException):
    def __init__(self, schedule_info: str, data_info: str) -> None:
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            f"Schedule with {schedule_info} has invalid {data_info} value",
        )


class ScheduleConflictedData(HTTPException):
    def __init__(self, first_data: str, second_data: str) -> None:
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            f"Schedule must have {first_data} value or {second_data} value, not both",
        )
