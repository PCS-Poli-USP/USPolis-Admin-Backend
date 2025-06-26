from datetime import datetime

from pydantic import BaseModel

from server.models.database.classroom_db_model import (
    Classroom,
)
from server.models.http.responses.schedule_response_models import ScheduleFullResponse
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.must_be_int import must_be_int


class ClassroomResponseBase(BaseModel):
    id: int
    name: str
    capacity: int
    floor: int
    accessibility: bool
    audiovisual: AudiovisualType
    air_conditioning: bool
    observation: str
    updated_at: datetime

    created_by_id: int
    created_by: str
    building_id: int
    building: str
    group_ids: list[int]
    groups: list[str]

    @classmethod
    def from_classroom(cls, classroom: Classroom) -> "ClassroomResponseBase":
        classroom_groups = classroom.get_groups()
        return cls(
            id=must_be_int(classroom.id),
            name=classroom.name,
            capacity=classroom.capacity,
            floor=classroom.floor,
            accessibility=classroom.accessibility,
            audiovisual=classroom.audiovisual,
            air_conditioning=classroom.air_conditioning,
            observation=classroom.observation,
            updated_at=classroom.updated_at,
            created_by_id=must_be_int(classroom.created_by_id),
            created_by=classroom.created_by.name,
            building_id=must_be_int(classroom.building_id),
            building=classroom.building.name,
            group_ids=[must_be_int(group.id) for group in classroom_groups],
            groups=[group.name for group in classroom_groups],
        )


class ClassroomResponse(ClassroomResponseBase):
    """Classroom commom response without schedules and occurrences"""

    @classmethod
    def from_classroom(cls, classroom: Classroom) -> "ClassroomResponse":
        base = ClassroomResponseBase.from_classroom(classroom)
        return cls(
            **base.model_dump(),
        )

    @classmethod
    def from_classroom_list(
        cls, classrooms: list[Classroom]
    ) -> list["ClassroomResponse"]:
        return [cls.from_classroom(classroom) for classroom in classrooms]


class ClassroomFullResponse(ClassroomResponseBase):
    """Classroom with schedules and occurrences"""

    schedules: list[ScheduleFullResponse]

    @classmethod
    def from_classroom(cls, classroom: Classroom) -> "ClassroomFullResponse":
        base = ClassroomResponseBase.from_classroom(classroom)
        return cls(
            **base.model_dump(),
            schedules=ScheduleFullResponse.from_schedule_list(classroom.schedules),
        )

    @classmethod
    def from_classroom_list(
        cls, classrooms: list[Classroom]
    ) -> list["ClassroomFullResponse"]:
        return [
            ClassroomFullResponse.from_classroom(classroom) for classroom in classrooms
        ]
