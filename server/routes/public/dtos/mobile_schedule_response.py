from datetime import date, time

from pydantic import BaseModel

from server.models.database.schedule_db_model import Schedule
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class MobileScheduleResponse(BaseModel):
    id: int
    week_day: str
    start_time: time
    end_time: time
    classroom: str | None = None
    building: str | None = None
    floor: int | None = None

    @classmethod
    def from_schedule(cls, schedule: Schedule) -> "MobileScheduleResponse":
        if schedule.id is None:
            raise UnfetchDataError("Schedule", "ID")
        return cls(
            id=schedule.id,
            week_day=WeekDay.to_str(schedule.week_day.value),
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            classroom=schedule.classroom.name if schedule.classroom else None,
            building=schedule.classroom.building.name if schedule.classroom else None,
            floor=schedule.classroom.floor if schedule.classroom else None
        )

    @classmethod
    def from_schedule_list(cls, schedules: list[Schedule]) -> list["MobileScheduleResponse"]:
        return [cls.from_schedule(schedule) for schedule in schedules]
    
    @classmethod
    def get_occurences_ids(cls, schedule: Schedule) -> list[int]:
        if schedule.occurrences is None:
            return []
        ids = []
        for occurence in schedule.occurrences:
            if occurence.id is None:
                raise UnfetchDataError("Ocurrence", "ID")
            ids.append(occurence.id)
        return ids