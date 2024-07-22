from datetime import datetime, time

from pydantic import BaseModel


class OccurrenceBase(BaseModel):
    schedule_id: int
    classroom_id: int | None = None
    start_time: time
    end_time: time


class OccurrenceRegister(OccurrenceBase):
    date: datetime


class OccurrenceUpdate(OccurrenceBase):
    date: datetime


class OccurenceManyRegister(OccurrenceBase):
    dates: list[datetime]