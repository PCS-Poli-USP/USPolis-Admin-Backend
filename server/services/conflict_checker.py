from datetime import date, time

from collections import defaultdict

from pydantic import BaseModel

from server.deps.authenticate import UserDep
from server.deps.repository_adapters.building_repository_adapter import (
    BuildingRepositoryDep,
)
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)
from server.deps.repository_adapters.schedule_repository_adapter import (
    ScheduleRepositoryDep,
)
from server.deps.session_dep import SessionDep
from server.models.database.classroom_db_model import (
    Classroom,
    ClassroomWithConflictsIndicator,
    ConflictsInfo,
)
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.occurrence_repository import OccurrenceRepository
from server.utils.must_be_int import must_be_int
from server.utils.occurrence_utils import OccurrenceUtils

Group = set[Occurrence]


class OccurrenceConflictSpecification(BaseModel):
    id: int
    start_time: time
    end_time: time
    date: date
    subject_code: str | None
    class_code: str | None
    class_id: int | None
    reservation_title: str | None
    reservation_id: int | None

    @classmethod
    def from_occurrence(
        cls, occurrence: Occurrence
    ) -> "OccurrenceConflictSpecification":
        return cls(
            id=must_be_int(occurrence.id),
            start_time=occurrence.start_time,
            end_time=occurrence.end_time,
            date=occurrence.date,
            subject_code=occurrence.schedule.class_.subject.code
            if occurrence.schedule.class_
            else None,
            class_code=occurrence.schedule.class_.code
            if occurrence.schedule.class_
            else None,
            class_id=must_be_int(occurrence.schedule.class_.id)
            if occurrence.schedule.class_
            else None,
            reservation_title=occurrence.schedule.reservation.title
            if occurrence.schedule.reservation
            else None,
            reservation_id=must_be_int(occurrence.schedule.reservation.id)
            if occurrence.schedule.reservation
            else None,
        )


class ClassroomConflictsSpecification(BaseModel):
    id: int
    name: str
    conflicts: dict[str, list]


class BuildingConflictSpecification(BaseModel):
    id: int
    name: str
    conflicts: list


class ConflictChecker:
    def __init__(
        self,
        user: UserDep,
        session: SessionDep,
        classroom_repository: ClassroomRepositoryDep,
        schedule_repository: ScheduleRepositoryDep,
        building_repository: BuildingRepositoryDep,
    ):
        self.user = user
        self.session = session
        self.classroom_repository = classroom_repository
        self.schedule_repository = schedule_repository
        self.building_repository = building_repository

    def conflicting_occurrences_by_classroom(self) -> dict[int, list[Group]]:
        classrooms = self.classroom_repository.get_all()
        grouped_occurrences: dict[int, list[Group]] = {}
        for classroom in classrooms:
            conflicting_occurrences = (
                self.__get_grouped_conflicting_occurrences_in_list(
                    classroom.occurrences
                )
            )
            if len(conflicting_occurrences) > 0:
                grouped_occurrences[must_be_int(classroom.id)] = conflicting_occurrences
        return grouped_occurrences

    def conflicting_occurrences_by_occurence(
        self, occurrence: Occurrence
    ) -> list[Occurrence]:
        """Returns a list of occurrences that conflict with the given occurrence"""
        if occurrence.classroom_id is None:
            return []
        occurrences = OccurrenceRepository.get_by_date_and_classroom(
            date=occurrence.date,
            classroom_id=occurrence.classroom_id,
            session=self.session,
        )
        conflicts = [
            oc
            for oc in occurrences
            if oc.id != occurrence.id
            and occurrence.conflicts_with_time(oc.start_time, oc.end_time)
        ]
        return conflicts

    def classrooms_with_conflicts_indicator_for_schedule(
        self, building_id: int, schedule_id: int
    ) -> list[ClassroomWithConflictsIndicator]:
        schedule = self.schedule_repository.get_by_id(schedule_id)
        classrooms = self.classroom_repository.get_all_on_building(building_id)

        classrooms_with_conflicts: list[ClassroomWithConflictsIndicator] = []
        for classroom in classrooms:
            total_count, infos = self.__count_conflicts_schedule_in_classroom(
                schedule, classroom
            )
            classroom_with_conflicts = ClassroomWithConflictsIndicator.from_classroom(
                classroom
            )
            classroom_with_conflicts.conflicts = total_count
            classroom_with_conflicts.conflicts_infos = infos
            classrooms_with_conflicts.append(classroom_with_conflicts)

        return classrooms_with_conflicts

    def classrooms_with_conflicts_indicator_for_time_and_dates(
        self, building_id: int, start_time: time, end_time: time, dates: list[date]
    ) -> list[ClassroomWithConflictsIndicator]:
        classrooms = ClassroomRepository.get_all_on_buildings(
            building_ids=[building_id], session=self.session
        )

        classrooms_with_conflicts: list[ClassroomWithConflictsIndicator] = []
        for classroom in classrooms:
            count = self.__count_conflicts_time_in_classroom_in_dates(
                start_time, end_time, dates, classroom
            )
            classroom_with_conflicts = ClassroomWithConflictsIndicator.from_classroom(
                classroom
            )
            classroom_with_conflicts.conflicts = count
            classrooms_with_conflicts.append(classroom_with_conflicts)

        return classrooms_with_conflicts

    def conflicts_for_allowed_classrooms(self) -> list[BuildingConflictSpecification]:
        classrooms_by_building = self.user.classrooms_by_buildings(session=self.session)
        result: list[BuildingConflictSpecification] = []
        for building, classrooms in classrooms_by_building.items():
            if not classrooms:
                continue
            on_building_result = BuildingConflictSpecification(
                id=must_be_int(building.id), name=building.name, conflicts=[]
            )
            for classroom in classrooms:
                conflicts = self.__conflicts_for_classroom(classroom)
                classroom_conflicts: dict[str, list] = defaultdict(list)
                for conflict in conflicts:
                    conflict_specs: list[OccurrenceConflictSpecification] = []
                    for occurrence in conflict:
                        conflict_specification = (
                            OccurrenceConflictSpecification.from_occurrence(occurrence)
                        )
                        conflict_specs.append(conflict_specification)
                    for conflict_spec in conflict_specs:
                        identifier = "N/A"
                        if (
                            conflict_spec.subject_code is not None
                            and conflict_spec.class_code is not None
                        ):
                            identifier = (
                                conflict_spec.subject_code
                                + " - "
                                + conflict_spec.class_code
                            )
                        if conflict_spec.reservation_title is not None:
                            identifier = conflict_spec.reservation_title
                        classroom_conflicts[identifier].append(conflict_specs)

                if classroom_conflicts:
                    on_building_result.conflicts.append(
                        ClassroomConflictsSpecification(
                            id=must_be_int(classroom.id),
                            name=classroom.name,
                            conflicts=classroom_conflicts,
                        )
                    )
            result.append(on_building_result)
        return result

    def __conflicts_for_classroom(self, classroom: Classroom) -> list[Group]:
        conflictings = self.__get_grouped_conflicting_occurrences_in_list(
            classroom.occurrences
        )
        return conflictings

    def __count_conflicts_schedule_in_classroom(
        self, schedule: Schedule, classroom: Classroom
    ) -> tuple[int, list[ConflictsInfo]]:
        total_count = 0
        occurrences_to_be_generated = OccurrenceUtils.generate_occurrences(schedule)
        infos: list[ConflictsInfo] = []
        for classroom_occurrence in classroom.occurrences:
            for schedule_occurrence in occurrences_to_be_generated:
                if classroom_occurrence.schedule_id == schedule.id:
                    continue
                schedule_occurrence.classroom_id = classroom.id
                if classroom_occurrence.conflicts_with(schedule_occurrence):
                    total_count += 1
                    schedule_id = classroom_occurrence.schedule_id
                    currente_schedule = classroom_occurrence.schedule
                    current_info = next(
                        (info for info in infos if info.schedule_id == schedule_id),
                        None,
                    )
                    if current_info is None:
                        current_info = ConflictsInfo.from_schedule(currente_schedule)
                        infos.append(current_info)
                    current_info.occurrence_ids.append(
                        must_be_int(classroom_occurrence.id)
                    )
                    current_info.conflicts_count += 1

        return total_count, infos

    def __count_conflicts_time_in_classroom(
        self, start_time: time, end_time: time, classroom: Classroom
    ) -> int:
        count = 0
        for classroom_occurrence in classroom.occurrences:
            if classroom_occurrence.conflicts_with_time(start_time, end_time):
                count += 1
        return count

    def __count_conflicts_time_in_classroom_in_dates(
        self, start_time: time, end_time: time, dates: list[date], classroom: Classroom
    ) -> int:
        count = 0
        filtered_occurrences = list(
            filter(lambda x: x.date in dates, classroom.occurrences)
        )
        for occurrence in filtered_occurrences:
            if occurrence.conflicts_with_time(start_time, end_time):
                count += 1
        return count

    def __get_grouped_conflicting_occurrences_in_list(
        self, occurrences: list[Occurrence]
    ) -> list[Group]:
        groups: list[Group] = []
        occurrence_group_map: dict[Occurrence, Group] = {}

        for i, occurrence in enumerate(occurrences):
            curr_group: Group | None = None
            for other_occurrence in occurrences[i + 1 :]:
                if occurrence.conflicts_with(other_occurrence):
                    if other_occurrence in occurrence_group_map:
                        other_group = occurrence_group_map[other_occurrence]
                        if curr_group is None:
                            curr_group = other_group
                            curr_group.add(occurrence)
                            occurrence_group_map[occurrence] = curr_group
                        else:
                            curr_group.update(other_group)
                            for item in other_group:
                                occurrence_group_map[item] = curr_group
                            groups.remove(other_group)
                    else:
                        if curr_group is None:
                            curr_group = {occurrence, other_occurrence}  # type: ignore
                            occurrence_group_map[occurrence] = curr_group
                            occurrence_group_map[other_occurrence] = curr_group
                            groups.append(curr_group)
                        else:
                            curr_group.add(other_occurrence)
                            occurrence_group_map[other_occurrence] = curr_group
        return groups
