from typing import TypedDict

from server.utils.enums.audiovisual_type_enum import AudiovisualType


class ClassroomBaseDict(TypedDict, total=False):

    name: str
    capacity: int
    floor: int
    ignore_to_allocate: bool
    accessibility: bool
    audiovisual: AudiovisualType
    air_conditioning: bool
