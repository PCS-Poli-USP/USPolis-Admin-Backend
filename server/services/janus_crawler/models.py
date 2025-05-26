from datetime import date, time
from pydantic import BaseModel
from server.utils.enums.week_day import WeekDay


class SubjectInfo(BaseModel):
    class_code: str
    subject_name: str
    subject_code: str
    total_students: int
    credits: int
    start_date: date
    end_date: date
    professors: list[str]

    start_time: time | None
    end_time: time | None
    week_day: WeekDay | None
