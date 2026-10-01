from datetime import date

from server.models.http.responses.occurrence_response_models import OccurrenceResponse
from tests.utils.academic_test_utils import make_building, make_classroom, make_occurrence
from tests.utils.time_test_utils import make_schedule


class TestOccurrenceResponse:
    def test_from_occurrence_with_a_classroom_and_label(self) -> None:
        classroom = make_classroom(building=make_building(), name="Sala 5")
        schedule = make_schedule(classroom=classroom)
        occurrence = make_occurrence(
            schedule=schedule,
            classroom=classroom,
            occurrence_date=date(2025, 3, 10),
            label="Prova final",
        )

        data = OccurrenceResponse.from_occurrence(occurrence)

        assert data.id == occurrence.id
        assert data.classroom_id == classroom.id
        assert data.classroom == "Sala 5"
        assert data.date == date(2025, 3, 10)
        assert data.label == "Prova final"

    def test_from_occurrence_without_a_classroom_or_label(self) -> None:
        schedule = make_schedule(classroom=None)
        occurrence = make_occurrence(schedule=schedule, classroom=None)

        data = OccurrenceResponse.from_occurrence(occurrence)

        assert data.classroom_id is None
        assert data.classroom is None
        assert data.label is None

    def test_from_occurrence_list(self) -> None:
        schedule = make_schedule()
        occurrence1 = make_occurrence(schedule=schedule, occurrence_date=date(2025, 1, 6))
        occurrence2 = make_occurrence(schedule=schedule, occurrence_date=date(2025, 1, 13))

        data = OccurrenceResponse.from_occurrence_list([occurrence1, occurrence2])

        assert [d.id for d in data] == [occurrence1.id, occurrence2.id]
