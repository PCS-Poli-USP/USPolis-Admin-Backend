from datetime import datetime
from typing import Annotated, Self

from beanie import Document, Indexed, Link
from fastapi import HTTPException


class Building(Document):
    name: Annotated[str, Indexed(unique=True)]
    created_by: Link["User"]  # type: ignore  # noqa: F821
    updated_at: datetime

    class Settings:
        name = "buildings"

    @classmethod
    async def by_ids(cls, ids: list[str]) -> list[Self]:
        async def get_building_by_id(id: str) -> Building:
            building = await Building.get(id)
            if not building:
                raise BuildingNotFound(id)
            return building

        return [await get_building_by_id(id) for id in ids]


class BuildingNotFound(HTTPException):
    def __init__(self, building_info: str) -> None:
        super().__init__(404, f"Building {building_info} not found")
