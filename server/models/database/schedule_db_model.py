from datetime import datetime

from beanie import Document, Link

from server.models.database.class_db_model import Class
from server.models.database.holiday_category_db_model import HolidayCategory
from server.utils.day_time import DayTime
from server.utils.recurrence import Recurrence
from server.utils.week_day import WeekDay


class Schedule(Document):
    university_class: Link[Class]
    week_day: WeekDay
    start_date: datetime
    end_date: datetime
    start_time: DayTime
    end_time: DayTime
    skip_exceptions: bool
    allocated: bool
    recurrence: Recurrence
    all_day: bool
    holiday_categories = list[Link[HolidayCategory]]

    class Settings:
        name = "schedules"  # Colletion Name
