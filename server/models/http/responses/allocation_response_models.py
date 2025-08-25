from pydantic import BaseModel
from datetime import time, date as datetime_date

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.http.responses.schedule_response_models import ScheduleResponseBase
from server.utils.enums.allocation_enum import AllocationEnum
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.reservation_type import ReservationType
from server.utils.enums.week_day import WeekDay
from server.utils.must_be_int import must_be_int


class RRule(BaseModel):
    # https://github.com/jkbrzt/rrule
    dtstart: str  # Must be YYYY-MM-DDTHH:mm:ss
    until: str  # Must be YYYY-MM-DDTHH:mm:ss
    freq: str
    interval: int
    byweekday: list[str]
    bysetpos: int | None = None

    @classmethod
    def from_schedule(cls, schedule: Schedule) -> "RRule":
        byweekday = []
        if schedule.week_day:
            byweekday.append(WeekDay.to_rrule(schedule.week_day.value))
        if schedule.recurrence == Recurrence.DAILY:
            byweekday = ["MO", "TH", "WE", "TU", "FR"]

        freq = schedule.recurrence.value.lower()
        if schedule.recurrence == Recurrence.BIWEEKLY:
            freq = "weekly"

        return cls(
            dtstart=f"{schedule.start_date}T{schedule.start_time}",
            until=f"{schedule.end_date}T{schedule.end_time}",
            freq=freq,
            interval=2 if schedule.recurrence == Recurrence.BIWEEKLY else 1,
            byweekday=byweekday,
            bysetpos=schedule.month_week.value if schedule.month_week else None,
        )


class BaseExtendedData(BaseModel):
    schedule_id: int
    occurrence_id: int | None = None
    building: str
    classroom: str
    classroom_capacity: int | None = None
    recurrence: Recurrence
    week_day: WeekDay | None = None
    month_week: MonthWeek | None = None
    start_time: time
    end_time: time
    start_date: datetime_date | None = None
    end_date: datetime_date | None = None

    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "BaseExtendedData":
        return cls(
            schedule_id=must_be_int(reservation.schedule.id),
            building=reservation.classroom.building.name,
            classroom=reservation.classroom.name,
            classroom_capacity=reservation.classroom.capacity,
            recurrence=reservation.schedule.recurrence,
            week_day=reservation.schedule.week_day,
            month_week=reservation.schedule.month_week,
            start_time=reservation.schedule.start_time,
            end_time=reservation.schedule.end_time,
            start_date=reservation.schedule.start_date,
            end_date=reservation.schedule.end_date,
        )

    @classmethod
    def from_class_schedule(cls, schedule: Schedule) -> "BaseExtendedData":
        return cls(
            schedule_id=must_be_int(schedule.id),
            building=schedule.classroom.building.name
            if schedule.classroom
            else AllocationEnum.UNALLOCATED.value,
            classroom=schedule.classroom.name
            if schedule.classroom
            else AllocationEnum.UNALLOCATED.value,
            classroom_capacity=schedule.classroom.capacity
            if schedule.classroom
            else None,
            recurrence=schedule.recurrence,
            week_day=schedule.week_day,
            month_week=schedule.month_week,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
        )


class ClassExtendedData(BaseExtendedData):
    class_id: int
    code: str
    subject_code: str
    subject_name: str
    allocated: bool
    professors: list[str]
    vacancies: int

    @classmethod
    def from_schedule(cls, schedule: Schedule) -> "ClassExtendedData":
        if schedule.class_ is None:
            raise ValueError("Schedule must have a class associated with it")

        base = BaseExtendedData.from_class_schedule(schedule)
        return cls(
            **base.model_dump(),
            class_id=must_be_int(schedule.class_.id),
            code=schedule.class_.code,
            subject_code=schedule.class_.subject.code,
            subject_name=schedule.class_.subject.name,
            allocated=schedule.allocated,
            professors=schedule.class_.professors,
            vacancies=schedule.class_.vacancies,
        )


class ReservationExtendedData(BaseExtendedData):
    reservation_id: int
    title: str
    type: ReservationType
    reason: str | None = None
    created_by: str

    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "ReservationExtendedData":
        base = BaseExtendedData.from_reservation(reservation)
        return cls(
            **base.model_dump(),
            reservation_id=must_be_int(reservation.id),
            title=reservation.title,
            type=reservation.type,
            reason=reservation.reason,
            created_by=reservation.created_by.name,
        )


class EventExtendedProps(BaseModel):
    class_data: ClassExtendedData | None = None
    reservation_data: ReservationExtendedData | None = None

    @classmethod
    def from_occurrence(cls, occurrence: Occurrence) -> "EventExtendedProps":
        data = cls()
        if occurrence.schedule.class_:
            data.class_data = ClassExtendedData.from_schedule(occurrence.schedule)
            data.class_data.occurrence_id = must_be_int(occurrence.id)
        if occurrence.schedule.reservation:
            data.reservation_data = ReservationExtendedData.from_reservation(
                occurrence.schedule.reservation
            )
            data.reservation_data.occurrence_id = must_be_int(occurrence.id)
        return data

    @classmethod
    def from_schedule(cls, schedule: Schedule) -> "EventExtendedProps":
        data = cls()
        if schedule.class_:
            data.class_data = ClassExtendedData.from_schedule(schedule)
        if schedule.reservation:
            data.reservation_data = ReservationExtendedData.from_reservation(
                schedule.reservation
            )
        return data


class AllocationEventResponse(BaseModel):
    id: str
    title: str
    start: str
    end: str

    classroom_id: int | None = None
    classroom: str | None = None
    classroom_capacity: int | None = None
    rrule: RRule | None = None
    allDay: bool

    resourceId: str
    extendedProps: EventExtendedProps | None = None

    @classmethod
    def from_occurrence(cls, occurrence: Occurrence) -> "AllocationEventResponse":
        resource = f"{AllocationEnum.UNALLOCATED_BUILDING_ID.value}-{
            AllocationEnum.UNALLOCATED_CLASSROOM_ID.value
        }"
        if occurrence.classroom:
            resource = (
                f"{occurrence.classroom.building.name}-{occurrence.classroom.name}"
            )
        title = ""
        if occurrence.schedule.class_:
            title = occurrence.schedule.class_.subject.code
        if occurrence.schedule.reservation:
            title = f"Reserva - {occurrence.schedule.reservation.title}"

        return cls(
            id=str(occurrence.id),
            title=title,
            start=f"{occurrence.date}T{occurrence.start_time}",
            end=f"{occurrence.date}T{occurrence.end_time}",
            classroom_id=occurrence.classroom_id,
            classroom=occurrence.classroom.name if occurrence.classroom else None,
            classroom_capacity=occurrence.classroom.capacity
            if occurrence.classroom
            else None,
            allDay=occurrence.schedule.all_day,
            resourceId=resource,
            extendedProps=EventExtendedProps.from_occurrence(occurrence),
        )

    @classmethod
    def from_schedule(cls, schedule: Schedule) -> list["AllocationEventResponse"]:
        resource = f"{AllocationEnum.UNALLOCATED_BUILDING_ID.value}-{
            AllocationEnum.UNALLOCATED_CLASSROOM_ID.value
        }"
        if schedule.classroom:
            resource = f"{schedule.classroom.building.name}-{schedule.classroom.name}"
        title = ""
        if schedule.class_:
            title = schedule.class_.subject.code
        if schedule.reservation:
            title = f"Reserva - {schedule.reservation.title}"
        if schedule.recurrence == Recurrence.CUSTOM:
            return [
                AllocationEventResponse.from_occurrence(occurrence)
                for occurrence in schedule.occurrences
            ]
        return [
            cls(
                id=str(schedule.id),
                title=title,
                start=f"{schedule.start_date}T{schedule.start_time}",
                end=f"{schedule.end_date}T{schedule.end_time}",
                classroom_id=schedule.classroom_id,
                classroom=schedule.classroom.name if schedule.classroom else None,
                rrule=RRule.from_schedule(schedule),
                allDay=schedule.all_day,
                resourceId=resource,
                extendedProps=EventExtendedProps.from_schedule(schedule),
            )
        ]

    @classmethod
    def from_occurrence_list(
        cls, occurrences: list[Occurrence]
    ) -> list["AllocationEventResponse"]:
        return [
            AllocationEventResponse.from_occurrence(occurrence)
            for occurrence in occurrences
        ]

    @classmethod
    def from_schedule_list(
        cls, schedules: list[Schedule]
    ) -> list["AllocationEventResponse"]:
        events = []
        for schedule in schedules:
            events.extend(AllocationEventResponse.from_schedule(schedule))
        return events


class AllocationResourceResponse(BaseModel):
    id: str
    parentId: str | None = None
    title: str

    @classmethod
    def from_building(cls, building: Building) -> list["AllocationResourceResponse"]:
        """Returns a list of resources, the first one is the building and the rest are the classrooms of the building"""
        resources: list[AllocationResourceResponse] = []
        resources.append(cls(id=building.name, title=building.name))
        classrooms_resources = AllocationResourceResponse.from_classroom_list(
            building.classrooms if building.classrooms else []
        )
        resources.extend(classrooms_resources)
        return resources

    @classmethod
    def from_building_list(
        cls, buildings: list[Building]
    ) -> list["AllocationResourceResponse"]:
        resources: list[AllocationResourceResponse] = []
        for building in buildings:
            resources.extend(AllocationResourceResponse.from_building(building))
        return resources

    @classmethod
    def from_classroom(cls, classroom: Classroom) -> "AllocationResourceResponse":
        return cls(
            id=f"{classroom.building.name}-{classroom.name}",
            parentId=str(classroom.building.name),
            title=classroom.name,
        )

    @classmethod
    def from_classroom_list(
        cls, classrooms: list[Classroom]
    ) -> list["AllocationResourceResponse"]:
        return [
            AllocationResourceResponse.from_classroom(classroom)
            for classroom in classrooms
            if not classroom.remote
        ]

    @classmethod
    def unnallocated_building(cls) -> "AllocationResourceResponse":
        return cls(
            id=AllocationEnum.UNALLOCATED_BUILDING_ID.value,
            title=AllocationEnum.UNALLOCATED.value,
        )

    @classmethod
    def unnallocated_classroom(cls) -> "AllocationResourceResponse":
        return cls(
            id=f"{AllocationEnum.UNALLOCATED_BUILDING_ID.value}-{AllocationEnum.UNALLOCATED_CLASSROOM_ID.value}",
            parentId=AllocationEnum.UNALLOCATED_BUILDING_ID.value,
            title=AllocationEnum.UNALLOCATED.value,
        )


class AllocationScheduleOptions(BaseModel):
    schedule_target_id: int
    schedule_target: ScheduleResponseBase
    options: list[ScheduleResponseBase]


class AllocationClassOptions(BaseModel):
    class_id: int
    class_code: str
    schedule_options: list[AllocationScheduleOptions]


class AllocationReuseTargetOptions(BaseModel):
    subject_id: int
    subject_code: str
    subject_name: str
    class_options: list[AllocationClassOptions]


class AllocationReuseResponse(BaseModel):
    building_id: int
    allocation_year: int
    target_options: list[AllocationReuseTargetOptions]
    strict: bool = True
