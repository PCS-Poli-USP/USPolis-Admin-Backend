from datetime import datetime

from pydantic import BaseModel

from server.models.database.building_db_model import Building


class BuildingResponse(BaseModel):
    name: str
    created_by: str
    updated_at: datetime

    @classmethod
    async def from_building(cls, building: Building) -> "BuildingResponse":
        return cls(
            name=building.name,
            created_by=building.created_by.name, # type: ignore
            updated_at=building.updated_at,
        )
