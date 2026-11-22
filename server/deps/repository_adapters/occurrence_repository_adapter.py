from typing import Annotated

from fastapi import Depends, HTTPException, status

from server.deps.access_scope_dep import AccessScopeDep
from server.deps.authenticate import UserDep
from server.deps.conflict_checker import ConflictCheckerDep
from server.deps.permission_index_dep import PermissionIndexDep
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)
from server.deps.repository_adapters.schedule_repository_adapter import (
    ScheduleRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.database.classroom_db_model import Classroom
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.allocate_request_models import AllocateSchedule
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.intentional_conflict_repository import (
    IntentionalConflictRepository,
)
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.schedule_repository import ScheduleRepository
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.services.security.occurrence_permission_checker import (
    OccurrencePermissionChecker,
)
from server.utils.enums.actions_enums import ClassroomAction


class OccurrenceRepositoryAdapter:
    def __init__(
        self,
        scope: AccessScopeDep,
        session: SessionDep,
        user: UserDep,
        classroom_repo: ClassroomRepositoryDep,
        schedule_repo: ScheduleRepositoryDep,
        conflict_checker: ConflictCheckerDep,
        permission_index: PermissionIndexDep,
    ):
        self.scope = scope
        self.session = session
        self.user = user
        self.classroom_repo = classroom_repo
        self.schedule_repo = schedule_repo
        self.checker = ClassroomPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )
        self.occurrence_checker = OccurrencePermissionChecker(
            user=user, session=session, permission_index=permission_index
        )
        self.conflict_checker = conflict_checker

    def get_all(self) -> list[Occurrence]:
        occurrences = OccurrenceRepository.get_all_on_buildings(
            building_ids=self.scope.readable_building_ids(), session=self.session
        )
        return occurrences

    def get_by_id(self, id: int) -> Occurrence:
        occurrence = OccurrenceRepository.get_by_id(id=id, session=self.session)
        self.occurrence_checker.check_permission(occurrence, ClassroomAction.READ)
        return occurrence

    def check_can_allocate(
        self,
        *,
        schedule: Schedule,
        current_classroom_id: int | None,
        target: Classroom | None,
    ) -> None:
        """The allocation rule, for schedules and single occurrences alike:

        - moving one takes ALLOCATE on the classroom it leaves and on the one it
          goes to; no grant on the class or its building is needed, so a
          classroom-level role allocates and deallocates in its own classrooms;
        - a class goes only into a classroom of one of its subject's buildings
          (a class has no building of its own: its subject is linked to
          buildings). This is a consistency rule, so it binds admins too: a
          class allocated outside its subject's buildings would be invisible
          to the people of that building.
        """
        if current_classroom_id is not None:
            self.checker.check_permission(
                current_classroom_id, ClassroomAction.ALLOCATE
            )
        if target is None:
            return
        self.checker.check_permission(target, ClassroomAction.ALLOCATE)
        class_ = schedule.class_
        if class_ is not None and target.building_id not in class_.building_ids():
            raise ClassroomOutsideSubjectBuildings(
                subject=class_.subject.code, classroom=target.name
            )

    def allocate_schedule(
        self, schedule_id: int, classroom_id: int, intentional_conflict: bool = False
    ) -> Schedule:
        schedule = ScheduleRepository.get_by_id(id=schedule_id, session=self.session)
        classroom = ClassroomRepository.get_by_id(id=classroom_id, session=self.session)
        self.check_can_allocate(
            schedule=schedule,
            current_classroom_id=schedule.classroom_id,
            target=classroom,
        )
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
            schedule = ScheduleRepository.get_by_id(
                id=pair.schedule_id, session=self.session
            )
            if pair.classroom_id == -1:
                self.check_can_allocate(
                    schedule=schedule,
                    current_classroom_id=schedule.classroom_id,
                    target=None,
                )
                OccurrenceRepository.remove_schedule_allocation(
                    user=self.user, schedule=schedule, session=self.session
                )
                continue

            classroom = ClassroomRepository.get_by_id(
                id=pair.classroom_id, session=self.session
            )
            self.check_can_allocate(
                schedule=schedule,
                current_classroom_id=schedule.classroom_id,
                target=classroom,
            )

            occurrences = OccurrenceRepository.allocate_schedule(
                user=self.user,
                schedule=schedule,
                classroom=classroom,
                session=self.session,
            )
            if pair.intentional_conflict and pair.intentional_occurrence_ids:
                intentional_occurrences = OccurrenceRepository.get_by_ids(
                    ids=pair.intentional_occurrence_ids, session=self.session
                )
                occurrences.sort(key=lambda x: x.date)
                for occurrence in occurrences:
                    for intentional_occurrence in intentional_occurrences:
                        if occurrence.conflicts_with(intentional_occurrence):
                            IntentionalConflictRepository.create(
                                first_occurrence=occurrence,
                                second_occurrence=intentional_occurrence,
                                session=self.session,
                            )

        self.session.commit()

    def remove_schedule_allocation(self, schedule_id: int) -> Schedule:
        schedule = ScheduleRepository.get_by_id(id=schedule_id, session=self.session)
        self.check_can_allocate(
            schedule=schedule,
            current_classroom_id=schedule.classroom_id,
            target=None,
        )
        OccurrenceRepository.remove_schedule_allocation(
            user=self.user, schedule=schedule, session=self.session
        )
        self.session.commit()
        self.session.refresh(schedule)
        return schedule

    def allocate_occurrence(self, occurrence: Occurrence, classroom: Classroom) -> None:
        self.check_can_allocate(
            schedule=occurrence.schedule,
            current_classroom_id=occurrence.classroom_id,
            target=classroom,
        )
        OccurrenceRepository.allocate_occurrence(occurrence, classroom, self.session)

    def remove_occurrence_allocation(self, occurrence: Occurrence) -> None:
        self.check_can_allocate(
            schedule=occurrence.schedule,
            current_classroom_id=occurrence.classroom_id,
            target=None,
        )
        OccurrenceRepository.remove_occurrence_allocation(occurrence, self.session)


class ClassroomOutsideSubjectBuildings(HTTPException):
    def __init__(self, *, subject: str, classroom: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"A disciplina {subject} não está no prédio da sala {classroom}: "
                "uma turma só pode ser alocada em salas dos prédios da sua "
                "disciplina. Adicione a disciplina ao prédio antes de alocar."
            ),
        )


OccurrenceRepositoryDep = Annotated[OccurrenceRepositoryAdapter, Depends()]
