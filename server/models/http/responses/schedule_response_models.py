from datetime import datetime
from pydantic import BaseModel

from server.models.database.schedule_db_model import Schedule
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.utils.day_time import DayTime
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class ScheduleResponseBase(BaseModel):
    id: int
    week_day: WeekDay | None
    start_date: datetime
    end_date: datetime
    start_time: DayTime
    end_time: DayTime
    skip_exceptions: bool
    allocated: bool
    recurrence: Recurrence
    all_day: bool


class ScheduleResponse(ScheduleResponseBase):
    occurrence_ids: list[int] | None

    class_id: int | None
    reservation_id: int | None

    classroom_id: int | None
    classroom: str | None

    building_id: int | None
    building: str | None

    @classmethod
    def from_schedule(cls, schedule: Schedule) -> "ScheduleResponse":
        if schedule.id is None:
            raise UnfetchDataError("Schedule", "ID")
        return cls(
            id=schedule.id,
            week_day=schedule.week_day,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
            start_time=DayTime.from_string(schedule.start_time),
            end_time=DayTime.from_string(schedule.end_time),
            skip_exceptions=schedule.skip_exceptions,
            allocated=schedule.allocated,
            recurrence=schedule.recurrence,
            all_day=schedule.all_day,
            classroom_id=schedule.classroom_id,
            classroom=schedule.classroom.name if schedule.classroom else None,
            building_id=schedule.classroom.building.id if schedule.classroom else None,
            building=schedule.classroom.building.name if schedule.classroom else None,
            class_id=schedule.class_id,
            reservation_id=schedule.reservation.id if schedule.reservation else None,
            occurrence_ids=cls.get_occurences_ids(schedule)
            if schedule.occurrences
            else None,
        )

    @classmethod
    def from_schedule_list(cls, schedules: list[Schedule]) -> list["ScheduleResponse"]:
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
