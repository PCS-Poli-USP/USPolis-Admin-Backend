from datetime import datetime
from enum import Enum
import re
from typing import List, Optional
from beanie import Document, Link
from pydantic import BaseModel, Field, validator

from database.models.university_class import Class
from database.models.subject import Subject


def validate_time_of_day(cls, value):
    if not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", value):
        raise ValueError("Invalid time format. Use HH:MM in 24-hour format.")
    return value


class WeekDay(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class Recurrence(Enum):
    SINGLE = "single"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class Schedule(Document):
    __collection__ = "schedules"
    university_class: Link[Class]
    week_day: WeekDay
    start_date: datetime
    end_date: datetime
    start_time: str
    end_time: str
    skip_exceptions: Optional[bool]
    allocated: Optional[bool]
    recurrence: Recurrence
    all_day: Optional[bool]
    # holiday_category: List[Link[HolidayCategory]]

    @validator("start_time", "end_time")
    def validate_time_of_day(cls, value):
        if not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", value):
            raise ValueError("Invalid time format. Use HH:MM in 24-hour format.")
        return value

    class Settings:
        validate_on_save = True
