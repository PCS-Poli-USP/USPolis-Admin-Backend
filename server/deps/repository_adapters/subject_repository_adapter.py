from typing import Annotated

from fastapi import Depends

from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.subject_db_model import Subject
from server.repositories.subject_repository import SubjectRepository


class SubjectRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
    ):
        self.owned_building_ids = owned_building_ids
        self.session = session

    def get_by_id(self, id: int) -> Subject:
        return SubjectRepository.get_by_id_on_buildings(
            id=id,
            building_ids=self.owned_building_ids,
            session=self.session,
        )

    def get_all(self) -> list[Subject]:
        return SubjectRepository.get_all_on_buildings(
            building_ids=self.owned_building_ids, session=self.session
        )


SubjectRepositoryDep = Annotated[SubjectRepositoryAdapter, Depends()]
