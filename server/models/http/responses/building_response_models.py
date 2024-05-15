from datetime import datetime

from pydantic import BaseModel

from server.models.database.building_db_model import Building


class BuildingResponse(BaseModel):
    id: str
    name: str
    created_by: str
    updated_at: datetime

    @classmethod
    async def from_building(cls, building: Building) -> "BuildingResponse":
        await building.fetch_all_links()
        return cls(
            id = str(building.id),
            name=building.name,
            created_by=building.created_by.name,  # type: ignore
            updated_at=building.updated_at,
        )

    @classmethod
    async def from_building_list(
        cls, buildings: list[Building]
    ) -> list["BuildingResponse"]:
        return [await cls.from_building(building) for building in buildings]
