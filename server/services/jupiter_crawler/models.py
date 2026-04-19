from datetime import datetime, time

from pydantic import BaseModel

from server.utils.enums.class_type import ClassType
from server.utils.enums.week_day import WeekDay


class GeneralInfo(BaseModel):
    class_code: str
    start_date: datetime
    end_date: datetime
    class_type: ClassType
    obs: str | None


class ScheduleInfo(BaseModel):
    week_day: WeekDay
    professors: list[str]
    start_time: time
    end_time: time


class StudentNumbersInfo(BaseModel):
    vacancies: int
    subscribers: int
    pendings: int
    enrolled: int


class JupiterScheduleSlot(BaseModel):
    week_day: WeekDay
    start_time: time
    end_time: time


class JupiterStudentSubject(BaseModel):
    code: str
    name: str
    available_days: list[JupiterScheduleSlot]
    observations: str = ""


class JupiterStudentSchedule(BaseModel):
    n_usp: str
    name: str
    email: str
    course: str
    institute: str
    subjects: list[JupiterStudentSubject]
