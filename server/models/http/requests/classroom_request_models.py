from pydantic import BaseModel


class ClassroomRegister(BaseModel):
    name: str
    building_id: str
    capacity: int
    floor: int
    ignore_to_allocate: bool
    accessibility: bool
    projector: bool
    air_conditioning: bool
