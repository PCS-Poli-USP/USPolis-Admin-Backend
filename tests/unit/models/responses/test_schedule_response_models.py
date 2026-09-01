from datetime import date

import pytest

from server.models.http.exceptions.responses_exceptions import UnfetchDataError
from server.models.http.responses.schedule_response_models import (
    ScheduleFullResponse,
    ScheduleResponse,
    ScheduleResponseBase,
)
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.week_day import WeekDay
from tests.utils.academic_test_utils import (
    make_allocation_log,
    make_building,
    make_class,
    make_classroom,
    make_occurrence,
    make_reservation,
    make_subject,
)
from tests.utils.time_test_utils import make_schedule


class TestScheduleResponseBase:
    def test_from_schedule_with_classroom_and_class(self) -> None:
        building = make_building(name="Bloco A")
        classroom = make_classroom(building=building, name="Sala 1")
        subject = make_subject(code="MAC0110", name="Introdução à Computação")
        class_ = make_class(subject=subject, code="T01")
        schedule = make_schedule(classroom=classroom, class_=class_)

        data = ScheduleResponseBase.from_schedule(schedule)

        assert data.classroom_id == classroom.id
        assert data.classroom == "Sala 1"
        assert data.building_id == building.id
        assert data.building == "Bloco A"
        assert data.class_id == class_.id
        assert data.subject == "Introdução à Computação"
        assert data.subject_code == "MAC0110"
        assert data.class_code == "T01"
        assert data.reservation_id is None
        assert data.reservation is None

    def test_from_schedule_without_classroom_or_class(self) -> None:
        schedule = make_schedule(classroom=None, class_=None)

        data = ScheduleResponseBase.from_schedule(schedule)

        assert data.classroom_id is None
        assert data.classroom is None
        assert data.building_id is None
        assert data.building is None
        assert data.class_id is None
        assert data.subject is None
        assert data.subject_code is None
        assert data.class_code is None

    def test_from_schedule_with_reservation(self) -> None:
        schedule = make_schedule()
        reservation = make_reservation(schedule=schedule, title="Reunião")

        data = ScheduleResponseBase.from_schedule(schedule)

        assert data.reservation_id == reservation.id
        assert data.reservation == "Reunião"

    def test_from_schedule_list(self) -> None:
        schedule1 = make_schedule()
        schedule2 = make_schedule()

        data = ScheduleResponseBase.from_schedule_list([schedule1, schedule2])

        assert [d.id for d in data] == [schedule1.id, schedule2.id]


class TestScheduleResponse:
    def test_custom_recurrence_includes_occurrences(self) -> None:
        schedule = make_schedule(recurrence=Recurrence.CUSTOM)
        occurrence = make_occurrence(schedule=schedule, occurrence_date=date(2025, 1, 6))
        schedule.occurrences = [occurrence]
        schedule.logs = []

        data = ScheduleResponse.from_schedule(schedule)

        assert data.occurrence_ids == [occurrence.id]
        assert data.occurrences is not None
        assert data.occurrences[0].id == occurrence.id

    def test_raises_when_an_occurrence_has_no_id(self) -> None:
        schedule = make_schedule(recurrence=Recurrence.CUSTOM)
        occurrence = make_occurrence(schedule=schedule, occurrence_date=date(2025, 1, 6))
        occurrence.id = None
        schedule.occurrences = [occurrence]
        schedule.logs = []

        with pytest.raises(UnfetchDataError):
            ScheduleResponse.from_schedule(schedule)

    def test_non_custom_recurrence_omits_occurrences(self) -> None:
        schedule = make_schedule(recurrence=Recurrence.WEEKLY)
        occurrence = make_occurrence(schedule=schedule)
        schedule.occurrences = [occurrence]
        schedule.logs = []

        data = ScheduleResponse.from_schedule(schedule)

        assert data.occurrence_ids is None
        assert data.occurrences is None

    def test_includes_last_log_when_present(self) -> None:
        schedule = make_schedule()
        schedule.occurrences = []
        log1 = make_allocation_log(schedule=schedule)
        log2 = make_allocation_log(schedule=schedule)
        schedule.logs = [log1, log2]

        data = ScheduleResponse.from_schedule(schedule)

        assert data.last_log is not None
        assert data.last_log.id == log1.id

    def test_no_logs_means_no_last_log(self) -> None:
        schedule = make_schedule()
        schedule.occurrences = []
        schedule.logs = []

        data = ScheduleResponse.from_schedule(schedule)

        assert data.last_log is None

    def test_from_schedule_list_sorts_by_week_day_none_last(self) -> None:
        schedule_friday = make_schedule(week_day=WeekDay.FRIDAY)
        schedule_friday.occurrences = []
        schedule_friday.logs = []
        schedule_monday = make_schedule(week_day=WeekDay.MONDAY)
        schedule_monday.occurrences = []
        schedule_monday.logs = []
        schedule_none = make_schedule(week_day=None, recurrence=Recurrence.DAILY)
        schedule_none.occurrences = []
        schedule_none.logs = []

        data = ScheduleResponse.from_schedule_list(
            [schedule_friday, schedule_none, schedule_monday]
        )

        assert [d.id for d in data] == [
            schedule_monday.id,
            schedule_friday.id,
            schedule_none.id,
        ]


class TestScheduleFullResponse:
    def test_from_schedule_always_includes_occurrences_and_logs(self) -> None:
        schedule = make_schedule()
        occurrence = make_occurrence(schedule=schedule)
        schedule.occurrences = [occurrence]
        log = make_allocation_log(schedule=schedule)
        schedule.logs = [log]

        data = ScheduleFullResponse.from_schedule(schedule)

        assert data.occurrences[0].id == occurrence.id
        assert data.logs[0].id == log.id

    def test_from_schedule_with_no_occurrences_returns_empty_list(self) -> None:
        schedule = make_schedule()
        schedule.occurrences = []
        schedule.logs = []

        data = ScheduleFullResponse.from_schedule(schedule)

        assert data.occurrences == []
        assert data.logs == []

    def test_from_schedule_list(self) -> None:
        schedule1 = make_schedule()
        schedule1.occurrences = []
        schedule1.logs = []
        schedule2 = make_schedule()
        schedule2.occurrences = []
        schedule2.logs = []

        data = ScheduleFullResponse.from_schedule_list([schedule1, schedule2])

        assert [d.id for d in data] == [schedule1.id, schedule2.id]
