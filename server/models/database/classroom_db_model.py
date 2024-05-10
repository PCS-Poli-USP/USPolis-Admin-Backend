from datetime import datetime
from typing import Self
from beanie import Document, Link
from fastapi import HTTPException, status
from bson import ObjectId
from pydantic import BaseModel

from server.models.database.building_db_model import Building
from server.models.database.user_db_model import User


class ClassroomSchedule(BaseModel):
    pass


class Classroom(Document):
    building: Link[Building]
    name: str
    capacity: int
    floor: int
    ignore_to_allocate: bool | None
    accessibility: bool
    projector: bool
    air_conditioning: bool
    created_by: Link[User]
    updated_at: datetime

    class Settings:
        name = "classrooms"
        indexes = [[("building", 1), ("name", 1)]]

    @classmethod
    async def by_id(cls, id: str) -> Self:
        classroom = await cls.get(id)
        if classroom is None:
            raise ClassroomNotFound(id)
        return classroom

    @classmethod
    async def by_building_and_classroom(
        cls, building_id: str, classroom_name: str
    ) -> Self:
        classroom = await cls.find_one(
            {"building.$id": ObjectId(building_id), "name": classroom_name}
        )
        if classroom is None:
            raise ClassroomInBuildingNotFound(classroom_name, building_id)
        return classroom

    @classmethod
    async def check_classroom_name_exists(
        cls, building_id: str, classroom_name: str
    ) -> bool:
        """Check if a classroom name exist in a building"""
        return (
            await cls.find_one(
                {"building.$id": ObjectId(building_id), "name": classroom_name}
            )
            is not None
        )

    @classmethod
    async def check_classroom_name_is_valid(
        cls, building_id: str, classroom_id: str, name: str
    ) -> bool:
        """Check if the classroom name is valid, i.e not used by other classroom in a building"""
        classroom = await cls.find_one(
            {"building.$id": ObjectId(building_id), "name": name}
        )
        if classroom is None:
            return True
        return str(classroom.id) == classroom_id


class ClassroomNotFound(HTTPException):
    def __init__(self, classroom_info: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND, f"Classroom {classroom_info} not found"
        )


class ClassroomInBuildingNotFound(HTTPException):
    def __init__(self, classroom_info: str, building_info: str) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"Classroom {classroom_info} in Building {building_info} not found",
        )
