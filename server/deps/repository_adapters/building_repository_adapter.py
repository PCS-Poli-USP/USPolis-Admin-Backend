from typing import Annotated
from fastapi import Depends
from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.models.http.requests.building_request_models import (
    BuildingRegister,
    BuildingUpdate,
)
from server.repositories.building_repository import BuildingRepository
from server.services.security.buildings_permission_checker import (
    building_permission_checker,
)


class BuildingRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
        user: UserDep,
    ):
        self.session = session
        self.user = user
        self.owned_building_ids = owned_building_ids

    def get_all(self) -> list[Building]:
        return BuildingRepository.get_by_ids(
            ids=self.owned_building_ids, session=self.session
        )

    def get_by_id(self, id: int) -> Building:
        building_permission_checker(self.user, id)
        building = BuildingRepository.get_by_id(id=id, session=self.session)
        return building

    def create(
        self,
        input: BuildingRegister,
    ) -> Building:
        building = BuildingRepository.create(
            building_in=input, creator=self.user, session=self.session
        )
        self.session.commit()
        self.session.refresh(building)
        return building

    def update(self, id: int, input: BuildingUpdate) -> Building:
        building = BuildingRepository.update(id=id, input=input, session=self.session)
        self.session.commit()
        self.session.refresh(building)
        return building

    def delete(self, id: int) -> None:
        BuildingRepository.delete(id=id, session=self.session)
        self.session.commit()

    def get_owned_buildings(self) -> list[Building]:
        buildings = BuildingRepository.get_by_ids(
            ids=self.owned_building_ids, session=self.session
        )
        return buildings


BuildingRepositoryDep = Annotated[BuildingRepositoryAdapter, Depends()]

BuildingRespositoryAdapterDep = Annotated[BuildingRepositoryAdapter, Depends()]
