from typing import Annotated

from fastapi import Depends, HTTPException, status

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.allocation_log_db_model import AllocationLog
from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.schedule_request_models import ScheduleRegister
from server.repositories.class_repository import ClassRepository
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.schedule_repository import ScheduleRepository
from server.services.security.class_permission_checker import ClassPermissionChecker
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.utils.must_be_int import must_be_int


class ScheduleRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        user: UserDep,
        session: SessionDep,
    ):
        self.owned_building_ids = owned_building_ids
        self.user = user
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

    def create_with_class(
        self,
        class_id: int,
        input: ScheduleRegister,
    ) -> Schedule:
        class_ = ClassRepository.get_by_id(id=class_id, session=self.session)
        checker = ClassPermissionChecker(user=self.user, session=self.session)
        checker.check_permission(class_)
        schedule = ScheduleRepository.create_with_class(
            class_=class_, input=input, session=self.session
        )
        if input.classroom_id:
            classroom = ClassroomRepository.get_by_id(
                id=input.classroom_id, session=self.session
            )
            ClassroomPermissionChecker(
                user=self.user, session=self.session
            ).check_permission(classroom)
            OccurrenceRepository.allocate_schedule(
                user=self.user,
                schedule=schedule,
                classroom=classroom,
                session=self.session,
            )
        self.session.commit()
        self.session.refresh(schedule)
        return schedule

    def create_many_with_class(
        self,
        inputs: list[ScheduleRegister],
    ) -> list[Schedule]:
        class_ids = [input.class_id for input in inputs if input.class_id is not None]
        if len(class_ids) != len(inputs):
            raise InvalidScheduleInput("Todas agendas devem se referir a uma turma.")
        return [
            self.create_with_class(class_id=must_be_int(input.class_id), input=input)
            for input in inputs
        ]


class InvalidScheduleInput(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


ScheduleRepositoryDep = Annotated[ScheduleRepositoryAdapter, Depends()]
