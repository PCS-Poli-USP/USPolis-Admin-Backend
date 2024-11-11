from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

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


class ClassroomBase(SQLModel):
    name: str
    capacity: int
    floor: int
    ignore_to_allocate: bool = False
    accessibility: bool = False
    projector: bool = False
    air_conditioning: bool = False
    updated_at: datetime = datetime.now()

    created_by_id: int = Field(foreign_key="user.id")
    building_id: int = Field(foreign_key="building.id")


class Classroom(ClassroomBase, table=True):
    __table_args__ = (
        UniqueConstraint(
            "name", "building_id", name="unique_classroom_name_for_building"
        ),
    )
    id: int | None = Field(primary_key=True, default=None)

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


class ClassroomWithConflictsIndicator(ClassroomBase):
    id: int
    conflicts: int = 0

    @classmethod
    def from_classroom(cls, classroom: Classroom) -> "ClassroomWithConflictsIndicator":
        return cls(
            id=must_be_int(classroom.id),
            name=classroom.name,
            capacity=classroom.capacity,
            floor=classroom.floor,
            ignore_to_allocate=classroom.ignore_to_allocate,
            accessibility=classroom.accessibility,
            projector=classroom.projector,
            air_conditioning=classroom.air_conditioning,
            updated_at=classroom.updated_at,
            created_by_id=classroom.created_by_id,
            building_id=classroom.building_id,
        )
