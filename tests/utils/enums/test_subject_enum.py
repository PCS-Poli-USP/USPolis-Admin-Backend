from datetime import datetime


class SubjectDefaultValues:
    CODE = "DEF0001"
    NAME: str = "default name"
    PROFESSORS: list[str] = ["default professor"]
    TYPE: str = "teorica"
    CLASS_CREDIT: int = 4
    WORK_CREDIT: int = 2
    ACTIVATION: datetime = datetime.now()
