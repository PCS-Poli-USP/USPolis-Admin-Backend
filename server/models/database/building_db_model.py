from datetime import datetime
from typing import Annotated, Self

from beanie import Document, Indexed, Link
from fastapi import HTTPException, status


class Building(Document):
    name: Annotated[str, Indexed(unique=True)]
    created_by: Link["User"]  # type: ignore  # noqa: F821
    updated_at: datetime

    class Settings:
        name = "buildings"

    @classmethod
    async def by_name(cls, name: str) -> Self | None:
        return await cls.find_one(cls.name == name)

    @classmethod
    async def by_id(cls, id: str) -> Self | None:
        return await cls.get(id)


class BuildingNameAlreadyExists(HTTPException):
    def __init__(self, building_name: str) -> None:
        super().__init__(status.HTTP_409_CONFLICT,
                         f"Building {building_name} already exists")
