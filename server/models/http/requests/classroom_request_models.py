from datetime import date, time

from pydantic import BaseModel

from server.utils.enums.audiovisual_type_enum import AudiovisualType


class ClassroomRegister(BaseModel):
    building_id: int
    # Legacy groups the classroom joins. Optional: creating a classroom takes
    # BuildingAction.CREATE on the building, which a role can grant.
    group_ids: list[int] = []

    name: str
    capacity: int
    floor: int
    accessibility: bool
    audiovisual: AudiovisualType
    air_conditioning: bool
    restricted: bool = False
    reservable: bool = True
    observation: str = ""


class ClassroomUpdate(ClassroomRegister):
    pass


class ClassroomConflictCheck(BaseModel):
    start_time: time
    end_time: time
    dates: list[date]
