from datetime import date, time

from pydantic import BaseModel


class OccurrenceBase(BaseModel):
    schedule_id: int | None = None
    classroom_id: int | None = None
    start_time: time
    end_time: time


class OccurrenceRegister(OccurrenceBase):
    date: date


class OccurrenceUpdate(OccurrenceBase):
    date: date


class OccurenceManyRegister(OccurrenceBase):
    dates: list[date]
