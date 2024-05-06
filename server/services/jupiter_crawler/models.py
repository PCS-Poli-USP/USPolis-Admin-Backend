from datetime import datetime

from pydantic import BaseModel

from server.utils.day_time import DayTime
from server.utils.enums.class_type import ClassType
from server.utils.enums.week_day import WeekDay


class CrawledSchedule(BaseModel):
    week_day: WeekDay
    start_date: datetime
    end_date: datetime
    start_time: DayTime
    end_time: DayTime


class CrawledCass(BaseModel):
    schedules: list[CrawledSchedule]
    start_date: datetime
    end_date: datetime
    class_type: ClassType
    vacancies: int
    subscribers: int
    pendings: int


class CrawledSubject(BaseModel):
    classes: list[CrawledCass]
    code: str
    name: str
    professors: list[str]
    type: str
    class_credit: int
    work_credit: int
    activation: datetime
    deactivation: datetime
