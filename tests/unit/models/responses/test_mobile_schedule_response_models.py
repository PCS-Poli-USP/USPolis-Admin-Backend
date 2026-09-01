from server.models.http.responses.mobile_schedule_response_models import (
    MobileScheduleResponse,
)
from server.utils.enums.week_day import WeekDay
from tests.utils.academic_test_utils import make_building, make_classroom, make_occurrence
from tests.utils.time_test_utils import make_schedule


class TestMobileScheduleResponseFromSchedule:
    def test_with_an_allocated_classroom(self) -> None:
        building = make_building(name="Bloco A")
        classroom = make_classroom(building=building, name="Sala 1")
        classroom.floor = 3
        schedule = make_schedule(week_day=WeekDay.MONDAY, classroom=classroom)

        data = MobileScheduleResponse.from_schedule(schedule)

        assert data.id == schedule.id
        assert data.week_day == WeekDay.to_str(WeekDay.MONDAY.value)
        assert data.classroom == "Sala 1"
        assert data.building == "Bloco A"
        assert data.floor == 3

    def test_without_a_classroom(self) -> None:
        schedule = make_schedule(week_day=WeekDay.MONDAY, classroom=None)

        data = MobileScheduleResponse.from_schedule(schedule)

        assert data.classroom is None
        assert data.building is None
        assert data.floor is None

    def test_without_a_week_day_defaults_to_empty_string(self) -> None:
        schedule = make_schedule(week_day=None)

        data = MobileScheduleResponse.from_schedule(schedule)

        assert data.week_day == ""

    def test_from_schedule_list(self) -> None:
        schedule1 = make_schedule(week_day=WeekDay.MONDAY)
        schedule2 = make_schedule(week_day=WeekDay.TUESDAY)

        data = MobileScheduleResponse.from_schedule_list([schedule1, schedule2])

        assert [d.id for d in data] == [schedule1.id, schedule2.id]


class TestGetOccurencesIds:
    def test_returns_empty_list_when_occurrences_is_none(self) -> None:
        schedule = make_schedule()
        # SQLAlchemy's instrumented relationship collection rejects a plain
        # `= None` assignment (it must stay list-like) even via
        # object.__setattr__, since the descriptor's __set__ still runs -
        # write straight into the instance dict to bypass that validation
        # and exercise this defensive branch at all.
        schedule.__dict__["occurrences"] = None # type: ignore

        ids = MobileScheduleResponse.get_occurences_ids(schedule)

        assert ids == []

    def test_returns_occurrence_ids(self) -> None:
        schedule = make_schedule()
        occurrence = make_occurrence(schedule=schedule)
        schedule.occurrences = [occurrence]

        ids = MobileScheduleResponse.get_occurences_ids(schedule)

        assert ids == [occurrence.id]
