from datetime import date, timedelta

from server.deps.interval_dep import QueryInterval
from server.models.http.responses.classroom_response_models import (
    ClassroomFullResponse,
    ClassroomResponse,
    ClassroomResponseBase,
)
from tests.utils.academic_test_utils import make_building, make_classroom
from tests.utils.time_test_utils import make_schedule


class TestClassroomResponseBase:
    def test_from_classroom(self) -> None:
        building = make_building(name="Bloco A")
        classroom = make_classroom(
            building=building, name="Sala 5", capacity=40, remote=False
        )

        data = ClassroomResponseBase.from_classroom(classroom)

        assert data.id == classroom.id
        assert data.name == "Sala 5"
        assert data.capacity == 40
        assert data.remote is False
        assert data.building_id == building.id
        assert data.building == "Bloco A"
        assert data.created_by_id == building.created_by_id
        assert data.created_by == building.created_by.name
        assert data.group_ids == []
        assert data.groups == []


class TestClassroomResponse:
    def test_from_classroom(self) -> None:
        classroom = make_classroom(building=make_building(), name="Sala 2")

        data = ClassroomResponse.from_classroom(classroom)

        assert data.id == classroom.id
        assert data.name == "Sala 2"

    def test_from_classroom_list(self) -> None:
        building = make_building()
        classroom1 = make_classroom(building=building, name="Sala 1")
        classroom2 = make_classroom(building=building, name="Sala 2")

        data = ClassroomResponse.from_classroom_list([classroom1, classroom2])

        assert [d.id for d in data] == [classroom1.id, classroom2.id]


class TestClassroomFullResponse:
    def test_includes_schedules_within_the_interval(self) -> None:
        classroom = make_classroom(building=make_building())
        today = date.today()
        schedule_in_range = make_schedule(
            classroom=classroom, start_date=today, end_date=today + timedelta(days=30)
        )
        schedule_out_of_range = make_schedule(
            classroom=classroom,
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=30),
        )
        schedule_in_range.occurrences = []
        schedule_in_range.logs = []
        schedule_out_of_range.occurrences = []
        schedule_out_of_range.logs = []
        classroom.schedules = [schedule_in_range, schedule_out_of_range]

        data = ClassroomFullResponse.from_classroom(classroom, interval=QueryInterval())

        schedule_ids = [s.id for s in data.schedules]
        assert schedule_in_range.id in schedule_ids
        assert schedule_out_of_range.id not in schedule_ids

    def test_from_classroom_list(self) -> None:
        building = make_building()
        classroom1 = make_classroom(building=building)
        classroom1.schedules = []
        classroom2 = make_classroom(building=building)
        classroom2.schedules = []

        data = ClassroomFullResponse.from_classroom_list([classroom1, classroom2])

        assert [d.id for d in data] == [classroom1.id, classroom2.id]
