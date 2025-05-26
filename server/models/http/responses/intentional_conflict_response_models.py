from datetime import time, date as datetime_date
from typing import TypedDict
from fastapi import HTTPException, status
from pydantic import BaseModel

from server.models.database.intentional_conflict_db_model import IntentionalConflict
from server.models.database.occurrence_db_model import Occurrence
from server.utils.must_be_int import must_be_int
from server.utils.type_guard import TypeGuard


class IntentionalConflictOccurrenceResponse(BaseModel):
    id: int
    label: str
    start_time: time
    end_time: time

    @classmethod
    def from_occurrence(
        cls, occurrence: Occurrence
    ) -> "IntentionalConflictOccurrenceResponse":
        schedule = occurrence.schedule
        id = schedule.class_id if schedule.class_id else schedule.reservation_id
        label = (
            schedule.class_.subject.name
            if schedule.class_
            else schedule.reservation.title
            if schedule.reservation
            else None
        )
        return cls(
            id=must_be_int(id),
            label=TypeGuard.must_be_str(label),
            start_time=occurrence.start_time,
            end_time=occurrence.end_time,
        )


class IntentionalConflictResponse(BaseModel):
    id: int
    classroom_id: int
    classroom: str
    date: datetime_date

    first_occurrence: IntentionalConflictOccurrenceResponse
    second_occurrence: IntentionalConflictOccurrenceResponse

    @classmethod
    def from_intentional_conflict(
        cls,
        conflict: IntentionalConflict,
    ) -> "IntentionalConflictResponse":
        first = conflict.first_occurrence
        if first.classroom is None:
            raise InvalidIntentionalConflict(detail="O conflito não possui sala")

        return cls(
            id=must_be_int(conflict.id),
            classroom_id=must_be_int(first.classroom_id),
            classroom=first.classroom.name,
            date=first.date,
            first_occurrence=IntentionalConflictOccurrenceResponse.from_occurrence(
                first
            ),
            second_occurrence=IntentionalConflictOccurrenceResponse.from_occurrence(
                conflict.second_occurrence
            ),
        )

    @classmethod
    def from_intentional_conflicts(
        cls,
        conflicts: list[IntentionalConflict],
    ) -> list["IntentionalConflictResponse"]:
        return [cls.from_intentional_conflict(conflict) for conflict in conflicts]


class ClassroomIntentionalConflictMapDict(TypedDict):
    classroom: str
    conflicts: list[IntentionalConflictResponse]


class ClassroomIntentionalConflictMap(BaseModel):
    classroom_id: int
    classroom: str
    conflicts: list[IntentionalConflictResponse]


class BuildingIntentionalConflictMapDict(TypedDict):
    building: str
    classroom_maps: dict[int, ClassroomIntentionalConflictMapDict]


class BuildingIntentionalConflictMap(BaseModel):
    building_id: int
    building: str
    classroom_maps: list[ClassroomIntentionalConflictMap]

    @classmethod
    def from_intentional_conflicts(
        cls,
        conflicts: list[IntentionalConflict],
    ) -> list["BuildingIntentionalConflictMap"]:
        building_conflicts: dict[int, BuildingIntentionalConflictMapDict] = {}
        for conflict in conflicts:
            first = conflict.first_occurrence
            classroom = first.classroom
            if classroom is None:
                raise InvalidIntentionalConflict(detail="O conflito não possui sala")

            building = classroom.building
            building_id = must_be_int(building.id)
            if building_id not in building_conflicts:
                building_conflicts[building_id] = {
                    "building": building.name,
                    "classroom_maps": {},
                }
            building_map = building_conflicts[building_id]
            classroom_maps = building_map["classroom_maps"]
            classroom_id = must_be_int(classroom.id)
            if classroom_id not in classroom_maps:
                classroom_maps[classroom_id] = {
                    "classroom": classroom.name,
                    "conflicts": [],
                }
            classroom_map = classroom_maps[classroom_id]
            classroom_map["conflicts"].append(
                IntentionalConflictResponse.from_intentional_conflict(conflict)
            )

        return [
            cls(
                building_id=b_id,
                building=b_map["building"],
                classroom_maps=[
                    ClassroomIntentionalConflictMap(
                        classroom_id=c_id,
                        classroom=c_map["classroom"],
                        conflicts=c_map["conflicts"],
                    )
                    for c_id, c_map in b_map["classroom_maps"].items()
                ],
            )
            for b_id, b_map in building_conflicts.items()
        ]


class InvalidIntentionalConflict(HTTPException):
    """Raised when an intentional conflict is invalid."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
