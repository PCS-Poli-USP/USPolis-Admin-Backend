from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import BuildingDep
from server.deps.session_dep import SessionDep
from server.models.database.schedule_db_model import Schedule
from server.repositories.classrooms_repository import ClassroomRepository
from server.repositories.occurrences_repository import OccurencesRepository
from server.repositories.schedule_repository import ScheduleRepository


class OccurrencesRepositoryAdapter:
    def __init__(self, building: BuildingDep, session: SessionDep):
        self.building = building
        self.session = session

    def allocate_schedule(self, schedule_id: int, classroom_id: int) -> Schedule:
        schedule = ScheduleRepository.get_by_id_on_building(
            schedule_id=schedule_id,
            building=self.building,
            session=self.session,
        )
        classroom = ClassroomRepository.get_by_id_on_building(
            building=self.building, id=classroom_id, session=self.session
        )
        OccurencesRepository.allocate_schedule(
            schedule=schedule, classroom=classroom, session=self.session
        )
        self.session.commit()
        self.session.refresh(schedule)
        return schedule

OccurrencesRepositoryDep = Annotated[OccurrencesRepositoryAdapter, Depends()]