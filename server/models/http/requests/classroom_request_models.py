from pydantic import BaseModel


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
