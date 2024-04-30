from datetime import datetime
from enum import Enum
from typing import List, Optional
from beanie import Document, Link
from pydantic import BaseModel

from database.models.university_class import Class
from database.models.subject import Subject


class WeekDay(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"


class Schedule(Document):
    university_class: Link[Class]
    week_day: WeekDay
    start_date: datetime

    class Settings:
        name = "schedules"  # Colletion Name
