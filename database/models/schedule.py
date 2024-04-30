from datetime import datetime
from enum import Enum
from typing import List
from beanie import Document, Link

from database.models.university_class import Class
from database.models.holiday_category import HolidayCategory


class WeekDay(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"


class Recurrence(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    BIWEEKLY = "Biweekly"
    MONTHLY = "Monthly"
    CUSTOM = "Custom"


class Schedule(Document):
    university_class: Link[Class]
    week_day: WeekDay
    start_date: datetime
    end_date: datetime
    start_time: str
    end_time: str
    skip_exceptions: bool
    allocated: bool
    recurrence: Recurrence
    all_day: bool
    holiday_categories = List[Link[HolidayCategory]]

    class Settings:
        name = "schedules"  # Colletion Name
