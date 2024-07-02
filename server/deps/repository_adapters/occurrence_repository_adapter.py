from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import BuildingDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)
from server.deps.repository_adapters.schedule_repository_adapter import (
    ScheduleRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.repositories.class_repository import ClassRepository
from server.repositories.occurrence_repository import OccurrenceRepository


class OccurrenceRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        building: BuildingDep,
        session: SessionDep,
        classroom_repo: ClassroomRepositoryDep,
        schedule_repo: ScheduleRepositoryDep,
    ):
        self.owned_building_ids = owned_building_ids
        self.building = building
        self.session = session
        self.classroom_repo = classroom_repo
        self.schedule_repo = schedule_repo

    def allocate_schedule(self, schedule_id: int, classroom_id: int) -> Schedule:
        schedule = self.schedule_repo.get_by_id(schedule_id)
        classroom = self.classroom_repo.get_by_id(classroom_id)
        OccurrenceRepository.allocate_schedule(
            schedule=schedule, classroom=classroom, session=self.session
        )
        self.session.commit()
        self.session.refresh(schedule)
        return schedule

    def allocate_class(self, class_id: int, classroom_id: int) -> Class:
        class_ = ClassRepository.get_by_id_on_building(
            id=class_id,
            building=self.building,
            session=self.session,
        )
        classroom = self.classroom_repo.get_by_id(classroom_id)
        OccurrenceRepository.allocate_class(
            class_=class_, classroom=classroom, session=self.session
        )
        self.session.commit()
        self.session.refresh(class_)
        return class_

    def remove_schedule_allocation(self, schedule_id: int) -> Schedule:
        schedule = self.schedule_repo.get_by_id(schedule_id)
        OccurrenceRepository.remove_schedule_allocation(
            schedule=schedule, session=self.session
        )
        self.session.commit()
        self.session.refresh(schedule)
        return schedule

    def remove_class_allocation(self, class_id: int) -> Class:
        class_ = ClassRepository.get_by_id_on_building(
            id=class_id,
            building=self.building,
            session=self.session,
        )
        OccurrenceRepository.remove_class_allocation(
            class_=class_, session=self.session
        )
        self.session.commit()
        self.session.refresh(class_)
        return class_


OccurrenceRepositoryDep = Annotated[OccurrenceRepositoryAdapter, Depends()]
