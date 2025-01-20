from pydantic import BaseModel
from datetime import time, date as datetime_date

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.utils.enums.allocation_enum import AllocationEnum
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.reservation_type import ReservationType
from server.utils.enums.week_day import WeekDay


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

        return cls(
            dtstart=f"{schedule.start_date}T{schedule.start_time}",
            until=f"{schedule.end_date}T{schedule.end_time}",
            freq=schedule.recurrence.value.lower(),
            interval=2 if schedule.recurrence == Recurrence.BIWEEKLY else 1,
            byweekday=byweekday,
            bysetpos=schedule.month_week.value if schedule.month_week else None,
        )


class BaseExtendedData(BaseModel):
    building: str
    classroom: str
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
            building=reservation.classroom.building.name,
            classroom=reservation.classroom.name,
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
            building=schedule.classroom.building.name
            if schedule.classroom
            else AllocationEnum.UNALLOCATED.value[0],
            classroom=schedule.classroom.name
            if schedule.classroom
            else AllocationEnum.UNALLOCATED.value[0],
            recurrence=schedule.recurrence,
            week_day=schedule.week_day,
            month_week=schedule.month_week,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
        )


class ClassExtendedData(BaseExtendedData):
    code: str
    subject_code: str
    subject_name: str
    allocated: bool
    professors: list[str]
    subscribers: int

    @classmethod
    def from_schedule(cls, schedule: Schedule) -> "ClassExtendedData":
        if schedule.class_ is None:
            raise ValueError("Schedule must have a class associated with it")

        base = BaseExtendedData.from_class_schedule(schedule)
        return cls(
            **base.model_dump(),
            code=schedule.class_.code,
            subject_code=schedule.class_.subject.code,
            subject_name=schedule.class_.subject.name,
            allocated=schedule.allocated,
            professors=schedule.class_.professors,
            subscribers=schedule.class_.subscribers,
        )


class ReservationExtendedData(BaseExtendedData):
    title: str
    type: ReservationType
    reason: str | None = None
    created_by: str

    @classmethod
    def from_reservation(cls, reservation: Reservation) -> "ReservationExtendedData":
        base = BaseExtendedData.from_reservation(reservation)
        return cls(
            **base.model_dump(),
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
        if occurrence.schedule.reservation:
            data.reservation_data = ReservationExtendedData.from_reservation(
                occurrence.schedule.reservation
            )
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


class EventResponse(BaseModel):
    id: str
    title: str
    start: str
    end: str

    classroom_id: int | None = None
    classroom: str | None = None
    rrule: RRule | None = None
    allDay: bool

    resourceId: str
    extendedProps: EventExtendedProps | None = None

    @classmethod
    def from_occurrence(cls, occurrence: Occurrence) -> "EventResponse":
        resource = AllocationEnum.UNALLOCATED_CLASSROOM_ID.value[0]
        if occurrence.schedule.classroom:
            resource = f"{
                occurrence.schedule.classroom.building.name}-{occurrence.schedule.classroom.name}"
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
            allDay=occurrence.schedule.all_day,
            resourceId=resource,
            extendedProps=EventExtendedProps.from_occurrence(occurrence),
        )

    @classmethod
    def from_schedule(cls, schedule: Schedule) -> "EventResponse":
        resource = f"{AllocationEnum.UNALLOCATED_BUILDING_ID.value[0]}-{
            AllocationEnum.UNALLOCATED_CLASSROOM_ID.value[0]}"
        if schedule.classroom:
            resource = f"{
                schedule.classroom.building.name}-{schedule.classroom.name}"
        title = ""
        if schedule.class_:
            title = schedule.class_.subject.code
        if schedule.reservation:
            title = f"Reserva - {schedule.reservation.title}"

        return cls(
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

    @classmethod
    def from_occurrence_list(
        cls, occurrences: list[Occurrence]
    ) -> list["EventResponse"]:
        return [EventResponse.from_occurrence(occurrence) for occurrence in occurrences]

    @classmethod
    def from_schedule_list(cls, schedules: list[Schedule]) -> list["EventResponse"]:
        return [EventResponse.from_schedule(schedule) for schedule in schedules]


class ResourceResponse(BaseModel):
    id: str
    parentId: str | None = None
    title: str

    @classmethod
    def from_building(cls, building: Building) -> list["ResourceResponse"]:
        """Returns a list of resources, the first one is the building and the rest are the classrooms of the building"""
        resources: list[ResourceResponse] = []
        resources.append(cls(id=building.name, title=building.name))
        classrooms_resources = ResourceResponse.from_classroom_list(
            building.classrooms if building.classrooms else []
        )
        resources.extend(classrooms_resources)
        return resources

    @classmethod
    def from_building_list(cls, buildings: list[Building]) -> list["ResourceResponse"]:
        resources: list[ResourceResponse] = []
        for building in buildings:
            resources.extend(ResourceResponse.from_building(building))
        return resources

    @classmethod
    def from_classroom(cls, classroom: Classroom) -> "ResourceResponse":
        return cls(
            id=f"{classroom.building.name}-{classroom.name}",
            parentId=str(classroom.building.name),
            title=classroom.name,
        )

    @classmethod
    def from_classroom_list(
        cls, classrooms: list[Classroom]
    ) -> list["ResourceResponse"]:
        return [ResourceResponse.from_classroom(classroom) for classroom in classrooms]

    @classmethod
    def unnallocated_building(cls) -> "ResourceResponse":
        return cls(
            id=AllocationEnum.UNALLOCATED_BUILDING_ID.value[0],
            title=AllocationEnum.UNALLOCATED.value[0],
        )

    @classmethod
    def unnallocated_classroom(cls) -> "ResourceResponse":
        return cls(
            id=f"{AllocationEnum.UNALLOCATED_BUILDING_ID.value[0]}-{AllocationEnum.UNALLOCATED_CLASSROOM_ID.value[0]}",
            parentId=AllocationEnum.UNALLOCATED_BUILDING_ID.value[0],
            title=AllocationEnum.UNALLOCATED.value[0],
        )
