from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import BuildingDep
from server.deps.session_dep import SessionDep
from server.models.database.class_db_model import Class
from server.models.database.schedule_db_model import Schedule
from server.repositories.class_repository import ClassRepository
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.schedule_repository import ScheduleRepository


class OccurrenceRepositoryAdapter:
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
        classroom = ClassroomRepository.get_by_id_on_building(
            building=self.building, id=classroom_id, session=self.session
        )
        OccurrenceRepository.allocate_class(
            class_=class_, classroom=classroom, session=self.session
        )
        self.session.commit()
        self.session.refresh(class_)
        return class_

    def remove_schedule_allocation(self, schedule_id: int) -> Schedule:
        schedule = ScheduleRepository.get_by_id_on_building(
            schedule_id=schedule_id,
            building=self.building,
            session=self.session,
        )
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
