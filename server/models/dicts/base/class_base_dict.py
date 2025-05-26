from datetime import date

from server.models.dicts.base.base_dict import BaseDict
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.class_type import ClassType


class ClassBaseDict(BaseDict, total=False):
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
