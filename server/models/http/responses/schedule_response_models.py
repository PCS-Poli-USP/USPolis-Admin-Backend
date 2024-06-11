from datetime import datetime
from pydantic import BaseModel

from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.classroom_response_models import ClassroomResponse
from server.models.http.responses.reservation_response_models import ReservationResponse
from server.utils.day_time import DayTime
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay


class ScheduleResponseBase(BaseModel):
    id: int
    week_day: WeekDay
    start_date: datetime
    end_date: datetime
    start_time: DayTime
    end_time: DayTime
    skip_exceptions: bool
    allocated: bool
    recurrence: Recurrence
    all_day: bool


class ScheduleResponse(ScheduleResponseBase):
    classroom: ClassroomResponse | None

    class_id: int | None

    reservation: ReservationResponse | None

    @classmethod
    def from_schedule(cls, schedule: Schedule) -> "ScheduleResponse":
        if schedule.id is None:
            raise UnfetchDataError("Schedule", "ID")
        return cls(
            id=schedule.id,
            week_day=schedule.week_day,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            skip_exceptions=schedule.skip_exceptions,
            allocated=schedule.allocated,
            recurrence=schedule.recurrence,
            all_day=schedule.all_day,
            classroom=ClassroomResponse.from_classroom(schedule.classroom)
            if schedule.classroom
            else None,
            class_id=schedule.university_class_id,
            reservation=ReservationResponse.from_reservation(schedule.reservation)
            if schedule.reservation
            else None,
        )

    @classmethod
    def from_schedule_list(cls, schedules: list[Schedule]) -> list["ScheduleResponse"]:
        return [cls.from_schedule(schedule) for schedule in schedules]
