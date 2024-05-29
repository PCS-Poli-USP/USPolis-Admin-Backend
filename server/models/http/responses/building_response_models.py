from datetime import datetime

from pydantic import BaseModel

from server.models.database.building_db_model import Building


class BuildingResponse(BaseModel):
    id: int
    name: str
    created_by: str
    updated_at: datetime

    @classmethod
    def from_building(cls, building: Building) -> "BuildingResponse":
        if building.id is None:
            raise ValueError(
                "Building ID is None, try refreshing the session if it is newly created"
            )
        return cls(
            id=building.id,
            name=building.name,
            created_by=building.created_by.name,
            updated_at=building.updated_at,
        )

    @classmethod
    def from_building_list(cls, buildings: list[Building]) -> list["BuildingResponse"]:
        return [cls.from_building(building) for building in buildings]
