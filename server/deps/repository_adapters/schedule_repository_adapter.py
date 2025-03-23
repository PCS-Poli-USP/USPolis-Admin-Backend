from typing import Annotated

from fastapi import Depends

from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.allocation_log_db_model import AllocationLog
from server.models.database.schedule_db_model import Schedule
from server.repositories.schedule_repository import ScheduleRepository


class ScheduleRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
    ):
        self.owned_building_ids = owned_building_ids
        self.session = session

    def get_by_id(self, schedule_id: int) -> Schedule:
        return ScheduleRepository.get_by_id_on_buildings(
            schedule_id=schedule_id,
            owned_building_ids=self.owned_building_ids,
            session=self.session,
        )

    def get_allocation_logs(self, schedule_id: int) -> list[AllocationLog]:
        schedule = ScheduleRepository.get_by_id_on_buildings(
            schedule_id=schedule_id,
            owned_building_ids=self.owned_building_ids,
            session=self.session,
        )
        return schedule.logs


ScheduleRepositoryDep = Annotated[ScheduleRepositoryAdapter, Depends()]
