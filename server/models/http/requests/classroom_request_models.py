from pydantic import BaseModel
from datetime import time, date


class ClassroomRegister(BaseModel):
    building_id: int
    name: str
    capacity: int
    floor: int
    ignore_to_allocate: bool
    accessibility: bool
    projector: bool
    air_conditioning: bool


class ClassroomUpdate(ClassroomRegister):
    pass


class ClassroomConflictCheck(BaseModel):
    start_time: time
    end_time: time
    dates: list[date]
