from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.deps.conflict_checker import ConflictCheckerDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)
from server.deps.repository_adapters.schedule_repository_adapter import (
    ScheduleRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.allocate_request_models import AllocateSchedule
from server.repositories.intentional_conflict_repository import (
    IntentionalConflictRepository,
)
from server.repositories.occurrence_repository import OccurrenceRepository
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.services.security.occurrence_permission_checker import (
    OccurrencePermissionChecker,
)
from server.services.security.schedule_permission_checker import (
    SchedulePermissionChecker,
)


class OccurrenceRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
        user: UserDep,
        classroom_repo: ClassroomRepositoryDep,
        schedule_repo: ScheduleRepositoryDep,
        conflict_checker: ConflictCheckerDep,
    ):
        self.owned_building_ids = owned_building_ids
        self.session = session
        self.user = user
        self.owned_building_ids = owned_building_ids
        self.classroom_repo = classroom_repo
        self.schedule_repo = schedule_repo
        self.checker = ClassroomPermissionChecker(user=user, session=session)
        self.occurrence_checker = OccurrencePermissionChecker(
            user=user, session=session
        )
        self.schedule_checker = SchedulePermissionChecker(user=user, session=session)
        self.conflict_checker = conflict_checker

    def get_all(self) -> list[Occurrence]:
        occurrences = OccurrenceRepository.get_all_on_buildings(
            building_ids=self.owned_building_ids, session=self.session
        )
        return occurrences

    def get_by_id(self, id: int) -> Occurrence:
        occurrence = OccurrenceRepository.get_by_id(id=id, session=self.session)
        self.occurrence_checker.check_permission(occurrence)
        return occurrence

    def allocate_schedule(
        self, schedule_id: int, classroom_id: int, intentional_conflict: bool = False
    ) -> Schedule:
        schedule = self.schedule_repo.get_by_id(schedule_id)
        classroom = self.classroom_repo.get_by_id(classroom_id)
        OccurrenceRepository.allocate_schedule(
            user=self.user,
            schedule=schedule,
            classroom=classroom,
            session=self.session,
        )

        self.session.commit()
        self.session.refresh(schedule)
        return schedule

    def allocate_schedule_many(
        self,
        schedule_classroom_pairs: list[AllocateSchedule],
    ) -> None:
        for pair in schedule_classroom_pairs:
            schedule = self.schedule_repo.get_by_id(pair.schedule_id)
            self.schedule_checker.check_permission(schedule)
            if pair.classroom_id == -1:
                OccurrenceRepository.remove_schedule_allocation(
                    user=self.user, schedule=schedule, session=self.session
                )
                continue

            classroom = self.classroom_repo.get_by_id(pair.classroom_id)
            self.checker.check_permission(classroom)

            occurrences = OccurrenceRepository.allocate_schedule(
                user=self.user,
                schedule=schedule,
                classroom=classroom,
                session=self.session,
            )
            if pair.intentional_conflict and pair.conflict_infos:
                for conflict_info in pair.conflict_infos:
                    pass
                for occurrence in occurrences:
                    conflicts = (
                        self.conflict_checker.conflicting_occurrences_by_occurence(
                            occurrence=occurrence
                        )
                    )
                    if conflicts:
                        IntentionalConflictRepository.create_many(
                            first_occurrence=occurrence,
                            second_occurrences=conflicts,
                            session=self.session,
                        )

        self.session.commit()

    def remove_schedule_allocation(self, schedule_id: int) -> Schedule:
        schedule = self.schedule_repo.get_by_id(schedule_id)
        OccurrenceRepository.remove_schedule_allocation(
            user=self.user, schedule=schedule, session=self.session
        )
        self.session.commit()
        self.session.refresh(schedule)
        return schedule


OccurrenceRepositoryDep = Annotated[OccurrenceRepositoryAdapter, Depends()]
