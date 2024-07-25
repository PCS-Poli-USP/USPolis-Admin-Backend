from typing import Annotated

from fastapi import Depends

from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.repositories.building_repository import BuildingRepository


class BuildingRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
    ):
        self.session = session
        self.owned_building_ids = owned_building_ids

    def get_owned_buildings(self) -> list[Building]:
        buildings = BuildingRepository.get_by_ids(
            ids=self.owned_building_ids, session=self.session
        )
        return buildings

BuildingRepositoryDep = Annotated[BuildingRepositoryAdapter, Depends()]