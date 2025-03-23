from datetime import time
from pydantic import BaseModel


class EventUpdate(BaseModel):
    desalocate: bool
    all_occurrences: bool
    start_time: time
    end_time: time
    building: str
    classroom: str
    occurrence_id: int | None
    schedule_id: int
