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
    async def by_building_and_classroom(cls, building_id: str, classroom_name: str) -> Self | None:
        return await cls.find_one({"building.$id" : ObjectId(building_id), "name" : classroom_name})


class ClassroomNotFound(HTTPException):
    def __init__(self, classroom_info: str) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND,
                         f"Classroom {classroom_info} not found")
