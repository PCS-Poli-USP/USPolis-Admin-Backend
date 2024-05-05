from datetime import datetime
from enum import Enum

from beanie import Document, Link

from server.models.database.class_db_model import Class
from server.models.database.holiday_category_db_model import HolidayCategory


class WeekDay(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thurday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


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
    holiday_categories = list[Link[HolidayCategory]]

    class Settings:
        name = "schedules"  # Colletion Name
