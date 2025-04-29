from datetime import date
from typing import TypedDict

from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.class_type import ClassType


class ClassBaseDict(TypedDict, total=False):
    """Base dict for class dictionaries (requests and database)"""

    start_date: date
    end_date: date
    code: str
    professors: list[str]
    type: ClassType
    vacancies: int

    air_conditionating: bool
    accessibility: bool
    audiovisual: AudiovisualType
    ignore_to_allocate: bool
