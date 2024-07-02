from typing import Any

from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.repository_adapters.classroom_repository_adapter import (
    ClassroomRepositoryDep,
)
from server.models.database.occurrence_db_model import Occurrence


class ConflictChecker:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        classroom_repository: ClassroomRepositoryDep,
    ):
        self.owned_building_ids = owned_building_ids
        self.classroom_repository = classroom_repository

    def conflicting_occurrences_by_classroom(self) -> Any:
        classrooms = self.classroom_repository.get_all()
        grouped_occurrences = {}
        for classroom in classrooms:
            occurrences = [occurrence for occurrence in classroom.occurrences]
            conflicting_occurrences = self.__get_conflicting_occurrences_in_list(
                occurrences
            )
            if conflicting_occurrences:
                grouped_occurrences[classroom.id] = conflicting_occurrences
        return grouped_occurrences

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
