from datetime import time
from pydantic import BaseModel

from server.utils.enums.week_day import WeekDay

class OccupanceReportsResponse(BaseModel):
    week_day: WeekDay
    classroom: str
    capacity: int
    classes: list[str]
    start_time: time
    end_time: time
    students: int
    percentage: float
