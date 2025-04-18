from pydantic import BaseModel
from datetime import time, date

from server.utils.enums.audiovisual_type_enum import AudiovisualType


class ClassroomRegister(BaseModel):
    building_id: int
    name: str
    capacity: int
    floor: int
    ignore_to_allocate: bool
    accessibility: bool
    audiovisual: AudiovisualType
    air_conditioning: bool


class ClassroomUpdate(ClassroomRegister):
    pass


class ClassroomConflictCheck(BaseModel):
    start_time: time
    end_time: time
    dates: list[date]
