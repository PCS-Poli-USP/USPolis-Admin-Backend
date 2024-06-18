from datetime import datetime
from pydantic import BaseModel

from server.utils.day_time import DayTime


class OccurrenceBase(BaseModel):
    schedule_id: int
    classroom_id: int | None = None
    start_time: DayTime
    end_time: DayTime


class OccurrenceRegister(OccurrenceBase):
    date: datetime


class OccurrenceUpdate(OccurrenceBase):
    date: datetime


class OccurenceManyRegister(OccurrenceBase):
    dates: list[datetime]
