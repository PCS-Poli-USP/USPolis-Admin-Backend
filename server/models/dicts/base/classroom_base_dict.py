from server.models.dicts.base.base_dict import BaseDict
from server.utils.enums.audiovisual_type_enum import AudiovisualType


class ClassroomBaseDict(BaseDict, total=False):
    """Base dict for classroom dictionaries (requests and database)"""

    name: str
    capacity: int
    floor: int
    accessibility: bool
    audiovisual: AudiovisualType
    air_conditioning: bool
    observation: str
    reservable: bool
    remote: bool
