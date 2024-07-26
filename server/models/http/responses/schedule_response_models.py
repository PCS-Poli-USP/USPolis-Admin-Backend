from datetime import date, time

from pydantic import BaseModel

from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.occurrence_response_models import OccurrenceResponse
from server.utils.enums import month_week
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class ScheduleResponseBase(BaseModel):
    id: int
    week_day: WeekDay | None = None
    month_week: MonthWeek | None = None
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    allocated: bool
    recurrence: Recurrence
    all_day: bool

    class_id: int | None = None
    reservation_id: int | None = None

    classroom_id: int | None = None
    classroom: str | None = None

    building_id: int | None = None
    building: str | None = None


class ScheduleResponse(ScheduleResponseBase):
    occurrence_ids: list[int] | None = None
    # When recurrence is custom is necessary
    occurrences: list[Occurrence] | None = None

    @classmethod
    def from_schedule(cls, schedule: Schedule) -> "ScheduleResponse":
        if schedule.id is None:
            raise UnfetchDataError("Schedule", "ID")
        return cls(
            id=schedule.id,
            week_day=schedule.week_day,
            month_week=schedule.month_week,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
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
            if schedule.occurrences and schedule.recurrence == Recurrence.CUSTOM
            else None,
            occurrences=schedule.occurrences
            if schedule.recurrence == Recurrence.CUSTOM
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


class ScheduleWithOccurrencesResponse(ScheduleResponseBase):
    occurrences: list[OccurrenceResponse]

    @classmethod
    def from_schedule(cls, schedule: Schedule) -> "ScheduleWithOccurrencesResponse":
        if schedule.id is None:
            raise UnfetchDataError("Schedule", "ID")
        return cls(
            id=schedule.id,
            week_day=schedule.week_day,
            month_week=schedule.month_week,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            allocated=schedule.allocated,
            recurrence=schedule.recurrence,
            all_day=schedule.all_day,
            classroom_id=schedule.classroom_id,
            classroom=schedule.classroom.name if schedule.classroom else None,
            building_id=schedule.classroom.building.id if schedule.classroom else None,
            building=schedule.classroom.building.name if schedule.classroom else None,
            class_id=schedule.class_id,
            reservation_id=schedule.reservation.id if schedule.reservation else None,
            occurrences=OccurrenceResponse.from_occurrence_list(schedule.occurrences) if schedule.occurrences else [],
        )

    @classmethod
    def from_schedule_list(cls, schedules: list[Schedule]) -> list["ScheduleWithOccurrencesResponse"]:
        return [cls.from_schedule(schedule) for schedule in schedules]
