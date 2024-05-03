from fastapi import HTTPException

from server.models.database.building_db_model import Building


class BuildingNotFound(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(404, detail)


async def get_buildings_by_ids(ids: list[str]) -> list[Building] | None:
    async def get_building_by_id(id: str) -> Building:
        building = await Building.get(id)
        if building is None:
            raise HTTPException(404, "Building not found")
        return building

    return [await get_building_by_id(id) for id in ids]
