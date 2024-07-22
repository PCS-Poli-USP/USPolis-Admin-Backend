from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)
from server.deps.repository_adapters.schedule_repository_adapter import (
    ScheduleRepositoryDep,
)
from server.models.database.classroom_db_model import (
    Classroom,
    ClassroomWithConflictsIndicator,
)
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.utils.must_be_int import must_be_int
from server.utils.occurrence_utils import OccurrenceUtils

Group = set[Occurrence]


class ConflictChecker:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        classroom_repository: ClassroomRepositoryDep,
        schedule_repository: ScheduleRepositoryDep,
    ):
        self.owned_building_ids = owned_building_ids
        self.classroom_repository = classroom_repository
        self.schedule_repository = schedule_repository

    def conflicting_occurrences_by_classroom(self) -> dict[int, list[Group]]:
        classrooms = self.classroom_repository.get_all()
        grouped_occurrences: dict[int, list[Group]] = {}
        for classroom in classrooms:
            conflicting_occurrences = (
                self.__get_grouped_conflicting_occurrences_in_list(
                    classroom.occurrences
                )
            )
            if conflicting_occurrences:
                grouped_occurrences[must_be_int(classroom.id)] = conflicting_occurrences
        return grouped_occurrences

    def classrooms_with_conflicts_indicator_for_schedule(
        self, building_id: int, schedule_id: int
    ) -> list[ClassroomWithConflictsIndicator]:
        schedule = self.schedule_repository.get_by_id(schedule_id)
        classrooms = self.classroom_repository.get_all_on_building(building_id)

        classrooms_with_conflicts: list[ClassroomWithConflictsIndicator] = []
        for classroom in classrooms:
            count = self.__count_conflicts_schedule_in_classroom(schedule, classroom)
            classroom_with_conflicts = ClassroomWithConflictsIndicator.from_classroom(
                classroom
            )
            classroom_with_conflicts.conflicts = count
            classrooms_with_conflicts.append(classroom_with_conflicts)

        return classrooms_with_conflicts

    def __count_conflicts_schedule_in_classroom(
        self, schedule: Schedule, classroom: Classroom
    ) -> int:
        count = 0
        occurrences_to_be_generated = OccurrenceUtils.occurrences_from_schedules(
            schedule
        )
        for classroom_occurrence in classroom.occurrences:
            for schedule_occurrence in occurrences_to_be_generated:
                if classroom_occurrence.schedule_id == schedule.id:
                    continue
                schedule_occurrence.classroom_id = classroom.id
                if classroom_occurrence.conflicts_with(schedule_occurrence):
                    count += 1
        return count

    def __get_conflicting_occurrences_in_list(
        self, occurrences: list[Occurrence]
    ) -> list[Occurrence]:
        conflicting_occurrences: set[Occurrence] = set()
        for i, occurrence in enumerate(occurrences):
            for other_occurrence in occurrences[i + 1 :]:
                if occurrence.conflicts_with(other_occurrence):
                    conflicting_occurrences.add(occurrence)
                    conflicting_occurrences.add(other_occurrence)
        return list(conflicting_occurrences)

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
                            curr_group = {occurrence, other_occurrence}
                            occurrence_group_map[occurrence] = curr_group
                            occurrence_group_map[other_occurrence] = curr_group
                            groups.append(curr_group)
                        else:
                            curr_group.add(other_occurrence)
                            occurrence_group_map[other_occurrence] = curr_group
        return groups
