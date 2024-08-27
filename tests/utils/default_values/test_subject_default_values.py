from datetime import datetime
from server.utils.enums.subject_type import SubjectType


class SubjectDefaultValues:
    CODE = "DEF0001"
    NAME: str = "default name"
    PROFESSORS: list[str] = ["default professor"]
    TYPE: SubjectType = SubjectType.BIANNUAL
    CLASS_CREDIT: int = 4
    WORK_CREDIT: int = 2
    ACTIVATION: datetime = datetime.now()
