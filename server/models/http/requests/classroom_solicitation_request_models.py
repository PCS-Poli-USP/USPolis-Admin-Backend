from pydantic import BaseModel
from datetime import time


class ClassroomSolicitationRegister(BaseModel):
    email: str
    classroom: str
    start_time: time
    end_time: time
    capacity: int


class ClassroomSolicitationUpdate(BaseModel):
    id: int
    