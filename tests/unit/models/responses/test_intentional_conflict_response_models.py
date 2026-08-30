import pytest

from server.models.http.responses.intentional_conflict_response_models import (
    BuildingIntentionalConflictMap,
    InvalidIntentionalConflict,
    IntentionalConflictOccurrenceResponse,
    IntentionalConflictResponse,
)
from tests.utils.academic_test_utils import (
    make_building,
    make_class,
    make_classroom,
    make_intentional_conflict,
    make_occurrence,
    make_reservation,
    make_subject,
)
from tests.utils.time_test_utils import make_schedule


class TestIntentionalConflictOccurrenceResponse:
    def test_from_occurrence_with_a_class(self) -> None:
        subject = make_subject(code="MAC0110", name="Introdução à Computação")
        class_ = make_class(subject=subject)
        schedule = make_schedule(class_=class_)
        occurrence = make_occurrence(schedule=schedule)

        data = IntentionalConflictOccurrenceResponse.from_occurrence(occurrence)

        assert data.id == class_.id
        assert data.label == "Introdução à Computação"

    def test_from_occurrence_with_a_reservation(self) -> None:
        schedule = make_schedule()
        reservation = make_reservation(schedule=schedule, title="Reunião")
        schedule.reservation_id = reservation.id
        occurrence = make_occurrence(schedule=schedule)

        data = IntentionalConflictOccurrenceResponse.from_occurrence(occurrence)

        assert data.id == reservation.id
        assert data.label == "Reunião"


class TestIntentionalConflictResponse:
    def test_from_intentional_conflict(self) -> None:
        building = make_building(name="Bloco A")
        classroom = make_classroom(building=building, name="Sala 1")
        subject = make_subject()
        class_ = make_class(subject=subject)
        schedule1 = make_schedule(classroom=classroom, class_=class_)
        occurrence1 = make_occurrence(schedule=schedule1, classroom=classroom)
        schedule2 = make_schedule(classroom=classroom, class_=class_)
        occurrence2 = make_occurrence(schedule=schedule2, classroom=classroom)
        conflict = make_intentional_conflict(
            first_occurrence=occurrence1, second_occurrence=occurrence2
        )

        data = IntentionalConflictResponse.from_intentional_conflict(conflict)

        assert data.id == conflict.id
        assert data.classroom_id == classroom.id
        assert data.classroom == "Sala 1"
        assert data.first_occurrence.id is not None
        assert data.second_occurrence.id is not None

    def test_raises_when_first_occurrence_has_no_classroom(self) -> None:
        schedule1 = make_schedule(classroom=None)
        occurrence1 = make_occurrence(schedule=schedule1, classroom=None)
        schedule2 = make_schedule()
        occurrence2 = make_occurrence(schedule=schedule2)
        conflict = make_intentional_conflict(
            first_occurrence=occurrence1, second_occurrence=occurrence2
        )

        with pytest.raises(InvalidIntentionalConflict):
            IntentionalConflictResponse.from_intentional_conflict(conflict)

    def test_from_intentional_conflicts(self) -> None:
        building = make_building()
        classroom = make_classroom(building=building)
        subject = make_subject()
        class_ = make_class(subject=subject)
        schedule1 = make_schedule(classroom=classroom, class_=class_)
        occurrence1 = make_occurrence(schedule=schedule1, classroom=classroom)
        schedule2 = make_schedule(classroom=classroom, class_=class_)
        occurrence2 = make_occurrence(schedule=schedule2, classroom=classroom)
        conflict = make_intentional_conflict(
            first_occurrence=occurrence1, second_occurrence=occurrence2
        )

        data = IntentionalConflictResponse.from_intentional_conflicts([conflict])

        assert [d.id for d in data] == [conflict.id]


class TestBuildingIntentionalConflictMap:
    def test_groups_conflicts_by_building_and_classroom(self) -> None:
        building = make_building(name="Bloco A")
        classroom = make_classroom(building=building, name="Sala 1")
        subject = make_subject()
        class_ = make_class(subject=subject)
        schedule1 = make_schedule(classroom=classroom, class_=class_)
        occurrence1 = make_occurrence(schedule=schedule1, classroom=classroom)
        schedule2 = make_schedule(classroom=classroom, class_=class_)
        occurrence2 = make_occurrence(schedule=schedule2, classroom=classroom)
        conflict = make_intentional_conflict(
            first_occurrence=occurrence1, second_occurrence=occurrence2
        )

        data = BuildingIntentionalConflictMap.from_intentional_conflicts([conflict])

        assert len(data) == 1
        assert data[0].building == "Bloco A"
        assert data[0].building_id == building.id
        assert len(data[0].classroom_maps) == 1
        assert data[0].classroom_maps[0].classroom == "Sala 1"
        assert [c.id for c in data[0].classroom_maps[0].conflicts] == [conflict.id]

    def test_raises_when_first_occurrence_has_no_classroom(self) -> None:
        schedule1 = make_schedule(classroom=None)
        occurrence1 = make_occurrence(schedule=schedule1, classroom=None)
        schedule2 = make_schedule()
        occurrence2 = make_occurrence(schedule=schedule2)
        conflict = make_intentional_conflict(
            first_occurrence=occurrence1, second_occurrence=occurrence2
        )

        with pytest.raises(InvalidIntentionalConflict):
            BuildingIntentionalConflictMap.from_intentional_conflicts([conflict])
