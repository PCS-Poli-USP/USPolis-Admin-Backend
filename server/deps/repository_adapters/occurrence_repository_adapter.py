from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)
from server.deps.repository_adapters.schedule_repository_adapter import (
    ScheduleRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.allocate_request_models import AllocateSchedule
from server.repositories.occurrence_repository import OccurrenceRepository
from server.services.security.buildings_permission_checker import (
    building_permission_checker,
)
from server.utils.must_be_int import must_be_int


class OccurrenceRepositoryAdapter:
    def __init__(
        self,
        session: SessionDep,
        user: UserDep,
        classroom_repo: ClassroomRepositoryDep,
        schedule_repo: ScheduleRepositoryDep,
    ):
        self.session = session
        self.user = user
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

    def allocate_schedule_many(
        self, schedule_classroom_pairs: list[AllocateSchedule]
    ) -> None:
        for pair in schedule_classroom_pairs:
            schedule = self.schedule_repo.get_by_id(pair.schedule_id)
            building_permission_checker(self.user, schedule.class_.subject.buildings)

            if pair.classroom_id == -1:
                OccurrenceRepository.remove_schedule_allocation(
                    schedule=schedule, session=self.session
                )
                continue

            classroom = self.classroom_repo.get_by_id(pair.classroom_id)
            building_permission_checker(self.user, must_be_int(classroom.building_id))

            OccurrenceRepository.allocate_schedule(
                schedule=schedule, classroom=classroom, session=self.session
            )
        self.session.commit()

    def remove_schedule_allocation(self, schedule_id: int) -> Schedule:
        schedule = self.schedule_repo.get_by_id(schedule_id)
        OccurrenceRepository.remove_schedule_allocation(
            schedule=schedule, session=self.session
        )
        self.session.commit()
        self.session.refresh(schedule)
        return schedule


OccurrenceRepositoryDep = Annotated[OccurrenceRepositoryAdapter, Depends()]
