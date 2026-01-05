from datetime import time
from pydantic import BaseModel

from server.services.occupance_reports_service import OccuppanceReportDict
from server.utils.enums.week_day import WeekDay


class OccupanceReportsResponse(BaseModel):
    week_day: WeekDay | None
    classroom: str
    capacity: int
    classes: list[str]
    start_time: time
    end_time: time
    students: int
    percentage: float
    class_id: list[int]

    @classmethod
    def from_dict(cls, value: OccuppanceReportDict) -> "OccupanceReportsResponse":
        return OccupanceReportsResponse(**value)

    @classmethod
    def from_dicts(
        cls, values: list[OccuppanceReportDict]
    ) -> list["OccupanceReportsResponse"]:
        return [OccupanceReportsResponse.from_dict(value) for value in values]
