from datetime import date, time

from collections import defaultdict
from typing import Self

from fastapi import HTTPException, status
from pydantic import BaseModel, model_validator

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
from server.models.database.intentional_conflict_db_model import IntentionalConflict
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.intentional_conflict_repository import (
    IntentionalConflictRepository,
)
from server.repositories.occurrence_repository import OccurrenceRepository
from server.utils.enums.confict_enum import ConflictType
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay
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


class ConflictParams(BaseModel):
    start_time: time
    end_time: time
    recurrence: Recurrence
    dates: list[date] = []
    start_date: date | None = None
    end_date: date | None = None
    week_day: WeekDay | None = None
    month_week: MonthWeek | None = None

    @model_validator(mode="after")
    def validate_body(self) -> Self:
        if self.recurrence != Recurrence.CUSTOM:
            if self.dates:
                raise InvalidConflictParams(
                    "Datas NÃO devem ser fornecidas para essa recorrência"
                )

            if not self.start_date or not self.end_date:
                raise InvalidConflictParams("Data de início e fim DEVEM ser fornecidas")

            if self.recurrence == Recurrence.DAILY and self.week_day:
                raise InvalidConflictParams(
                    "Dia da semana NÃO deve ser fornecida para essa recorrência"
                )

            if not self.week_day:
                raise InvalidConflictParams(
                    "Dia da semana DEVE ser fornecida para essa recorrência"
                )

            if (
                self.recurrence == Recurrence.WEEKLY
                or self.recurrence == Recurrence.BIWEEKLY
            ) and self.month_week:
                raise InvalidConflictParams(
                    "Semana do mês NÃO deve ser fornecida para essa recorrência"
                )

            if self.recurrence == Recurrence.MONTHLY and not self.month_week:
                raise InvalidConflictParams(
                    "Semana do mês DEVE ser fornecida para essa recorrência"
                )

        if self.recurrence == Recurrence.CUSTOM and not self.dates:
            raise InvalidConflictParams(
                "Datas DEVEM ser fornecidas para essa recorrência"
            )
        return self


class InvalidConflictParams(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


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

    def classrooms_with_conflicts_indicator_for_schedule(
        self,
        building_id: int,
        schedule_id: int,
    ) -> list[ClassroomWithConflictsIndicator]:
        schedule = self.schedule_repository.get_by_id(schedule_id)
        classrooms = self.classroom_repository.get_all_on_building(building_id)

        classrooms_with_conflicts: list[ClassroomWithConflictsIndicator] = []
        for classroom in classrooms:
            total_count, infos = (
                self.__calculate_conflicts_info_for_schedule_in_classroom(
                    schedule,
                    classroom,
                )
            )
            classroom_with_conflicts = ClassroomWithConflictsIndicator.from_classroom(
                classroom
            )
            classroom_with_conflicts.conflicts = total_count
            classroom_with_conflicts.conflicts_infos = infos
            classrooms_with_conflicts.append(classroom_with_conflicts)

        return classrooms_with_conflicts

    def classrooms_with_conflicts_indicator(
        self,
        building_id: int,
        params: ConflictParams,
    ) -> list[ClassroomWithConflictsIndicator]:
        classrooms = ClassroomRepository.get_all_on_buildings(
            building_ids=[building_id], session=self.session
        )
        dates = params.dates
        if params.recurrence != Recurrence.CUSTOM:
            dates = OccurrenceUtils._dates_for_recurrence(
                week_day=params.week_day.value if params.week_day else -1,
                recurrence=params.recurrence,
                start_date=params.start_date,  # type: ignore
                end_date=params.end_date,  # type: ignore
                month_week=params.month_week.value if params.month_week else None,
            )
        classrooms_with_conflicts: list[ClassroomWithConflictsIndicator] = []
        for classroom in classrooms:
            count = self.__count_conflicts_time_in_classroom_in_dates(
                params.start_time,
                params.end_time,
                dates,
                classroom,
            )
            classroom_with_conflicts = ClassroomWithConflictsIndicator.from_classroom(
                classroom
            )
            classroom_with_conflicts.conflicts = count
            classrooms_with_conflicts.append(classroom_with_conflicts)

        return classrooms_with_conflicts

    def specificate_conflicts_for_allowed_classrooms(
        self, start: date, end: date, type: ConflictType
    ) -> list[BuildingConflictSpecification]:
        classrooms_by_building = self.user.classrooms_by_buildings(session=self.session)
        result: list[BuildingConflictSpecification] = []
        for building, classrooms in classrooms_by_building.items():
            if not classrooms:
                continue
            on_building_result = BuildingConflictSpecification(
                id=must_be_int(building.id), name=building.name, conflicts=[]
            )
            for classroom in classrooms:
                if classroom.remote:
                    continue
                conflicts = self.calculate_conflicts_for_allowed_classroom(
                    classroom=classroom,
                    start=start,
                    end=end,
                    type=type,
                )
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

    def calculate_conflicts_for_allowed_classroom(
        self,
        classroom: Classroom,
        start: date,
        end: date,
        type: ConflictType,
    ) -> list[Group]:
        if type == ConflictType.INTENTIONAL:
            return self.__intentional_conflicts_for_classroom(classroom, start, end)
        return self.__unintentional_conflicts_for_classroom(classroom, start, end)

    def __get_classroom_occurrences_by_range(
        self,
        classroom_id: int,
        start_date: date,
        end_date: date,
    ) -> list[Occurrence]:
        occurrences = OccurrenceRepository.get_all_on_interval_for_classroom(
            classroom_id=classroom_id,
            start=start_date,
            end=end_date,
            session=self.session,
        )
        return occurrences

    def __get_intentional_conflicts_for_classroom(
        self,
        classroom: Classroom,
        start: date,
        end: date,
    ) -> list[IntentionalConflict]:
        intentional = IntentionalConflictRepository.get_all_on_classroom_by_range(
            classroom_id=must_be_int(classroom.id),
            start=start,
            end=end,
            session=self.session,
        )
        return intentional

    def __get_intentional_pairs_for_classroom(
        self, classroom: Classroom, start: date, end: date
    ) -> set[tuple[Occurrence, Occurrence]]:
        intentional = IntentionalConflictRepository.get_all_on_classroom_by_range(
            classroom_id=must_be_int(classroom.id),
            start=start,
            end=end,
            session=self.session,
        )
        intentional_pairs = set(
            [(i.first_occurrence, i.second_occurrence) for i in intentional]
        )
        return intentional_pairs

    def __unintentional_conflicts_for_classroom(
        self,
        classroom: Classroom,
        start: date,
        end: date,
    ) -> list[Group]:
        occurrences = self.__get_classroom_occurrences_by_range(
            must_be_int(classroom.id), start, end
        )
        intentional_pairs = self.__get_intentional_pairs_for_classroom(
            classroom, start, end
        )
        conflictings = self.__get_grouped_unintentional_conflicting_occurrences_in_list(
            occurrences,
            intentional_pairs,
        )
        return conflictings

    def __intentional_conflicts_for_classroom(
        self,
        classroom: Classroom,
        start: date,
        end: date,
    ) -> list[Group]:
        intentional = self.__get_intentional_conflicts_for_classroom(
            classroom, start, end
        )
        firsts = set([i.first_occurrence for i in intentional])
        seconds = set([i.second_occurrence for i in intentional])
        intentional_occurrences = set(firsts).union(set(seconds))
        intentional_pairs = set(
            [(i.first_occurrence, i.second_occurrence) for i in intentional]
        )
        conflictings = self.__get_grouped_intentional_conflicting_occurrences_in_list(
            list(intentional_occurrences),
            intentional_pairs,
        )
        return conflictings

    def __get_occurrences_for_schedule(self, schedule: Schedule) -> list[Occurrence]:
        if schedule.allocated:
            return schedule.occurrences
        return OccurrenceUtils.generate_occurrences(schedule)

    def __calculate_conflicts_info_for_schedule_in_classroom(
        self, schedule: Schedule, classroom: Classroom
    ) -> tuple[int, list[ConflictsInfo]]:
        total_count = 0
        infos: list[ConflictsInfo] = []
        schedule_occurrences = self.__get_occurrences_for_schedule(schedule)
        occurrences = self.__get_classroom_occurrences_by_range(
            must_be_int(classroom.id), schedule.start_date, schedule.end_date
        )
        intentional_conflicts = (
            IntentionalConflictRepository.get_all_on_classroom_by_range(
                classroom_id=must_be_int(classroom.id),
                start=schedule.start_date,
                end=schedule.end_date,
                session=self.session,
            )
        )
        pair_ids = set(
            [
                (i.first_occurrence_id, i.second_occurrence_id)
                for i in intentional_conflicts
            ]
        )

        for classroom_occurrence in occurrences:
            for schedule_occurrence in schedule_occurrences:
                if classroom_occurrence.schedule_id == schedule.id:
                    continue

                schedule_id = classroom_occurrence.schedule_id
                current_schedule = classroom_occurrence.schedule
                current_info = next(
                    (info for info in infos if info.schedule_id == schedule_id),
                    None,
                )

                if (classroom_occurrence.id, schedule_occurrence.id) in pair_ids:
                    if current_info is None:
                        current_info = ConflictsInfo.from_schedule(current_schedule)
                        infos.append(current_info)
                    current_info.intentional_ids.append(
                        must_be_int(classroom_occurrence.id)
                    )
                    current_info.intentional_count += 1
                    current_info.total_count += 1
                    pair_ids.remove((classroom_occurrence.id, schedule_occurrence.id))  # type: ignore
                elif (schedule_occurrence.id, classroom_occurrence.id) in pair_ids:
                    if current_info is None:
                        current_info = ConflictsInfo.from_schedule(current_schedule)
                        infos.append(current_info)
                    current_info.intentional_ids.append(
                        must_be_int(classroom_occurrence.id)
                    )
                    current_info.intentional_count += 1
                    current_info.total_count += 1
                    pair_ids.remove((schedule_occurrence.id, classroom_occurrence.id))  # type: ignore
                else:
                    if classroom_occurrence.conflicts_with_time_and_date(
                        schedule_occurrence.start_time,
                        schedule_occurrence.end_time,
                        schedule_occurrence.date,
                    ):
                        total_count += 1
                        if current_info is None:
                            current_info = ConflictsInfo.from_schedule(current_schedule)
                            infos.append(current_info)
                        current_info.unintentional_ids.append(
                            must_be_int(classroom_occurrence.id)
                        )
                        current_info.unintentional_count += 1
                        current_info.total_count += 1

        return total_count, infos

    def __get_filtered_occurrences_by_dates(
        self,
        classroom: Classroom,
        dates: list[date],
    ) -> list[Occurrence]:
        filtered_occurrences = list(
            filter(lambda x: x.date in dates, classroom.occurrences)
        )
        return filtered_occurrences

    def __count_conflicts_time_in_classroom_in_dates(
        self,
        start_time: time,
        end_time: time,
        dates: list[date],
        classroom: Classroom,
    ) -> int:
        count = 0
        filtered_occurrences = self.__get_filtered_occurrences_by_dates(
            classroom, dates
        )
        for occurrence in filtered_occurrences:
            if occurrence.conflicts_with_time(start_time, end_time):
                count += 1
        return count

    def __pair_exists_in_intentional_pairs(
        self,
        first_occurrence: Occurrence,
        second_occurrence: Occurrence,
        intentional_pairs: set[tuple[Occurrence, Occurrence]],
    ) -> bool:
        return (first_occurrence, second_occurrence) in intentional_pairs or (
            second_occurrence,
            first_occurrence,
        ) in intentional_pairs

    def __insert_pair_in_group_map(
        self,
        occurrence: Occurrence,
        other_occurrence: Occurrence,
        curr_group: Group | None,
        groups: list[Group],
        occurrence_group_map: dict[Occurrence, Group],
    ) -> None:
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
                curr_group = {occurrence, other_occurrence}  # pyright: ignore[reportUnhashable]
                occurrence_group_map[occurrence] = curr_group
                occurrence_group_map[other_occurrence] = curr_group
                groups.append(curr_group)
            else:
                curr_group.add(other_occurrence)
                occurrence_group_map[other_occurrence] = curr_group

    def __get_grouped_intentional_conflicting_occurrences_in_list(
        self,
        occurrences: list[Occurrence],
        intentional_pairs: set[tuple[Occurrence, Occurrence]],
    ) -> list[Group]:
        groups: list[Group] = []
        occurrence_group_map: dict[Occurrence, Group] = {}
        for i, occurrence in enumerate(occurrences):
            curr_group: Group | None = None
            for other_occurrence in occurrences[i + 1 :]:
                if self.__pair_exists_in_intentional_pairs(
                    occurrence, other_occurrence, intentional_pairs
                ) and occurrence.conflicts_with(other_occurrence):
                    self.__insert_pair_in_group_map(
                        occurrence,
                        other_occurrence,
                        curr_group,
                        groups,
                        occurrence_group_map,
                    )

        return groups

    def __get_grouped_unintentional_conflicting_occurrences_in_list(
        self,
        occurrences: list[Occurrence],
        intentional_pairs: set[tuple[Occurrence, Occurrence]],
    ) -> list[Group]:
        groups: list[Group] = []
        occurrence_group_map: dict[Occurrence, Group] = {}
        for i, occurrence in enumerate(occurrences):
            curr_group: Group | None = None
            for other_occurrence in occurrences[i + 1 :]:
                if not self.__pair_exists_in_intentional_pairs(
                    occurrence, other_occurrence, intentional_pairs
                ) and occurrence.conflicts_with(other_occurrence):
                    self.__insert_pair_in_group_map(
                        occurrence,
                        other_occurrence,
                        curr_group,
                        groups,
                        occurrence_group_map,
                    )
        return groups
