from datetime import datetime

from pydantic import BaseModel

from server.models.database.classroom_db_model import (
    Classroom,
)
from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.occurrence_response_models import OccurrenceResponse
from server.models.http.responses.schedule_response_models import ScheduleResponse


class ClassroomResponseBase(BaseModel):
    id: int
    name: str
    capacity: int
    floor: int
    ignore_to_allocate: bool
    accessibility: bool
    projector: bool
    air_conditioning: bool
    updated_at: datetime


class ClassroomResponse(ClassroomResponseBase):
    created_by_id: int
    created_by: str
    building_id: int
    building: str

    @classmethod
    def from_classroom(cls, classroom: Classroom) -> "ClassroomResponse":
        if classroom.id is None:
            raise UnfetchDataError("Classroom", "ID")
        if classroom.created_by_id is None:
            raise UnfetchDataError("Classroom", "created_by_id")
        if classroom.building_id is None:
            raise UnfetchDataError("Classroom", "building_id")
        return cls(
            id=classroom.id,
            name=classroom.name,
            capacity=classroom.capacity,
            floor=classroom.floor,
            ignore_to_allocate=classroom.ignore_to_allocate,
            accessibility=classroom.accessibility,
            projector=classroom.projector,
            air_conditioning=classroom.air_conditioning,
            updated_at=classroom.updated_at,
            created_by_id=classroom.created_by_id,
            created_by=classroom.created_by.name,
            building_id=classroom.building_id,
            building=classroom.building.name,
        )

    @classmethod
    def from_classroom_list(
        cls, classrooms: list[Classroom]
    ) -> list["ClassroomResponse"]:
        return [cls.from_classroom(classroom) for classroom in classrooms]


class ClassroomWithSchedulesResponse(ClassroomResponse):
    schedules: list[ScheduleResponse]
    occurrences: list[OccurrenceResponse]

    @classmethod
    def from_classroom(cls, classroom: Classroom) -> "ClassroomWithSchedulesResponse":
        if classroom.id is None:
            raise UnfetchDataError("Classroom", "ID")
        if classroom.created_by_id is None:
            raise UnfetchDataError("Classroom", "created_by_id")
        if classroom.building_id is None:
            raise UnfetchDataError("Classroom", "building_id")
        if classroom.schedules is None:
            raise UnfetchDataError("Classroom", "Schedules")

        return cls(
            id=classroom.id,
            name=classroom.name,
            capacity=classroom.capacity,
            floor=classroom.floor,
            ignore_to_allocate=classroom.ignore_to_allocate,
            accessibility=classroom.accessibility,
            projector=classroom.projector,
            air_conditioning=classroom.air_conditioning,
            updated_at=classroom.updated_at,
            created_by_id=classroom.created_by_id,
            created_by=classroom.created_by.name,
            building_id=classroom.building_id,
            building=classroom.building.name,
            schedules=ScheduleResponse.from_schedule_list(classroom.schedules),
            occurrences=OccurrenceResponse.from_occurrence_list(classroom.occurrences),
        )
