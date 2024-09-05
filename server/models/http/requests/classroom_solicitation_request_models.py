from pydantic import BaseModel
from datetime import time


class ClassroomSolicitationRegister(BaseModel):
    classroom_id: int
    building_id: int
    email: str
    start_time: time
    end_time: time
    capacity: int


class ClassroomSolicitationUpdate(BaseModel):
    id: int
