from datetime import datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, Column, Enum
from server.models.database.base_db_model import BaseModel
from pydantic import BaseModel as PydanticBaseModel

from server.models.database.group_classroom_link import GroupClassroomLink
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.must_be_int import must_be_int

if TYPE_CHECKING:
    from server.models.database.building_db_model import Building
    from server.models.database.occurrence_db_model import Occurrence
    from server.models.database.reservation_db_model import Reservation
    from server.models.database.schedule_db_model import Schedule
    from server.models.database.user_db_model import User
    from server.models.database.classroom_solicitation_db_model import (
        ClassroomSolicitation,
    )
    from server.models.database.group_db_model import Group


class ClassroomBase(BaseModel):
    name: str
    capacity: int
    floor: int
    accessibility: bool = False
    audiovisual: AudiovisualType = Field(
        sa_column=Column(Enum(AudiovisualType), nullable=False)
    )
    air_conditioning: bool = False
    updated_at: datetime = Field(default_factory=BrazilDatetime.now_utc)

    created_by_id: int = Field(foreign_key="user.id")
    building_id: int = Field(foreign_key="building.id")


class Classroom(ClassroomBase, table=True):
    __table_args__ = (
        UniqueConstraint(
            "name", "building_id", name="unique_classroom_name_for_building"
        ),
    )

    created_by: "User" = Relationship()
    building: "Building" = Relationship(back_populates="classrooms")
    occurrences: list["Occurrence"] = Relationship(back_populates="classroom")
    reservations: list["Reservation"] = Relationship(
        back_populates="classroom", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    schedules: list["Schedule"] = Relationship(back_populates="classroom")
    solicitations: list["ClassroomSolicitation"] = Relationship(
        back_populates="classroom"
    )
    groups: list["Group"] = Relationship(
        back_populates="classrooms", link_model=GroupClassroomLink
    )


class ConflictsInfo(PydanticBaseModel):
    subject_id: int | None
    subject: str | None
    class_id: int | None
    class_code: str | None
    reservation: str | None
    reservation_id: int | None
    schedule_id: int
    start: time
    end: time
    total_count: int
    intentional_ids: list[int]
    intentional_count: int
    unintentional_ids: list[int]
    unintentional_count: int

    @classmethod
    def from_schedule(cls, schedule: "Schedule") -> "ConflictsInfo":
        return cls(
            subject_id=must_be_int(schedule.class_.subject_id)
            if schedule.class_
            else None,
            subject=schedule.class_.subject.code if schedule.class_ else None,
            class_id=must_be_int(schedule.class_.id) if schedule.class_ else None,
            class_code=schedule.class_.code if schedule.class_ else None,
            reservation=schedule.reservation.title if schedule.reservation else None,
            reservation_id=must_be_int(schedule.reservation.id)
            if schedule.reservation
            else None,
            schedule_id=must_be_int(schedule.id),
            start=schedule.start_time,
            end=schedule.end_time,
            total_count=0,
            intentional_ids=[],
            intentional_count=0,
            unintentional_ids=[],
            unintentional_count=0,
        )


class ClassroomWithConflictsIndicator(ClassroomBase):
    conflicts: int = 0
    conflicts_infos: list[ConflictsInfo] = []

    @classmethod
    def from_classroom(cls, classroom: Classroom) -> "ClassroomWithConflictsIndicator":
        return cls(
            id=must_be_int(classroom.id),
            name=classroom.name,
            capacity=classroom.capacity,
            floor=classroom.floor,
            accessibility=classroom.accessibility,
            audiovisual=classroom.audiovisual,
            air_conditioning=classroom.air_conditioning,
            updated_at=classroom.updated_at,
            created_by_id=classroom.created_by_id,
            building_id=classroom.building_id,
        )
