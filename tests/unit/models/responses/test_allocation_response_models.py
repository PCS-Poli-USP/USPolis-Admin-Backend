from datetime import date

import pytest

from server.models.http.responses.allocation_response_models import (
    AllocationEventResponse,
    AllocationResourceResponse,
    BaseExtendedData,
    ClassExtendedData,
    EventExtendedProps,
    ReservationExtendedData,
    RRule,
)
from server.utils.enums.allocation_enum import AllocationEnum
from server.utils.enums.allocation_event_type_enum import AllocationEventType
from server.utils.enums.month_week import MonthWeek
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.reservation_type import ReservationType
from server.utils.enums.week_day import WeekDay
from tests.utils.academic_test_utils import (
    make_building,
    make_class,
    make_classroom,
    make_exam,
    make_occurrence,
    make_reservation,
    make_solicitation,
    make_subject,
    make_user,
)
from tests.utils.time_test_utils import make_schedule


class TestRRule:
    def test_weekly_schedule(self) -> None:
        schedule = make_schedule(recurrence=Recurrence.WEEKLY, week_day=WeekDay.TUESDAY)
        rrule = RRule.from_schedule(schedule)
        assert rrule.freq == "weekly"
        assert rrule.interval == 1
        assert rrule.byweekday == ["TU"]
        assert rrule.bysetpos is None
        assert rrule.dtstart == "2025-01-01T08:00:00"
        assert rrule.until == "2025-06-30T10:00:00"

    def test_biweekly_schedule_uses_weekly_freq_with_interval_two(self) -> None:
        schedule = make_schedule(recurrence=Recurrence.BIWEEKLY, week_day=WeekDay.FRIDAY)
        rrule = RRule.from_schedule(schedule)
        assert rrule.freq == "weekly"
        assert rrule.interval == 2
        assert rrule.byweekday == ["FR"]

    def test_daily_schedule_uses_all_weekdays(self) -> None:
        schedule = make_schedule(recurrence=Recurrence.DAILY, week_day=None)
        rrule = RRule.from_schedule(schedule)
        assert rrule.freq == "daily"
        assert rrule.byweekday == ["MO", "TH", "WE", "TU", "FR"]

    def test_monthly_schedule_sets_bysetpos_from_month_week(self) -> None:
        schedule = make_schedule(
            recurrence=Recurrence.MONTHLY,
            week_day=WeekDay.MONDAY,
            month_week=MonthWeek.FIRST,
        )
        rrule = RRule.from_schedule(schedule)
        assert rrule.freq == "monthly"
        assert rrule.bysetpos == MonthWeek.FIRST.value


class TestBaseExtendedDataFromReservation:
    def test_with_an_allocated_classroom(self) -> None:
        building = make_building()
        classroom = make_classroom(building=building, name="Sala 5", capacity=50)
        schedule = make_schedule(classroom=classroom)
        reservation = make_reservation(schedule=schedule)

        data = BaseExtendedData.from_reservation(reservation)

        assert data.building == building.name
        assert data.classroom == "Sala 5"
        assert data.classroom_capacity == 50

    def test_without_a_classroom_falls_back_to_solicitation_building(self) -> None:
        building = make_building()
        schedule = make_schedule(classroom=None)
        user = make_user()
        solicitation = make_solicitation(building=building, user=user)
        reservation = make_reservation(schedule=schedule, solicitation=solicitation)

        data = BaseExtendedData.from_reservation(reservation)

        assert data.building == building.name
        assert data.classroom == AllocationEnum.UNALLOCATED.value
        assert data.classroom_capacity is None


class TestBaseExtendedDataFromClassSchedule:
    def test_with_a_classroom(self) -> None:
        building = make_building()
        classroom = make_classroom(building=building)
        schedule = make_schedule(classroom=classroom)

        data = BaseExtendedData.from_class_schedule(schedule)

        assert data.building == building.name
        assert data.classroom == classroom.name

    def test_without_a_classroom(self) -> None:
        schedule = make_schedule(classroom=None)

        data = BaseExtendedData.from_class_schedule(schedule)

        assert data.building == AllocationEnum.UNALLOCATED.value
        assert data.classroom == AllocationEnum.UNALLOCATED.value
        assert data.classroom_capacity is None


class TestClassExtendedData:
    def test_raises_when_schedule_has_no_class(self) -> None:
        schedule = make_schedule(class_=None)
        with pytest.raises(ValueError, match="must have a class"):
            ClassExtendedData.from_schedule(schedule)

    def test_builds_from_a_schedule_with_a_class(self) -> None:
        subject = make_subject(code="MAC0110")
        class_ = make_class(subject=subject, code="T01", vacancies=35)
        schedule = make_schedule(class_=class_)

        data = ClassExtendedData.from_schedule(schedule)

        assert data.class_id == class_.id
        assert data.code == "T01"
        assert data.subject_code == "MAC0110"
        assert data.vacancies == 35


class TestReservationExtendedData:
    def test_without_an_exam(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(classroom=classroom)
        reservation = make_reservation(schedule=schedule, type_=ReservationType.MEETING)

        data = ReservationExtendedData.from_reservation(reservation)

        assert data.reservation_id == reservation.id
        assert data.type == ReservationType.MEETING
        assert data.subject_id is None
        assert data.class_ids is None

    def test_with_an_exam(self) -> None:
        subject = make_subject(code="MAC0110")
        class_ = make_class(subject=subject)
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(classroom=classroom)
        reservation = make_reservation(schedule=schedule, type_=ReservationType.EXAM)
        make_exam(reservation=reservation, subject=subject, classes=[class_])

        data = ReservationExtendedData.from_reservation(reservation)

        assert data.subject_id == subject.id
        assert data.subject_code == "MAC0110"
        assert data.class_ids == [class_.id]
        assert data.class_codes == [class_.code]


class TestEventExtendedProps:
    def test_from_occurrence_with_class_only(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        schedule = make_schedule(class_=class_)
        occurrence = make_occurrence(schedule=schedule, label="Prova final")

        props = EventExtendedProps.from_occurrence(occurrence)

        assert props.class_data is not None
        assert props.class_data.occurrence_id == occurrence.id
        assert props.class_data.label == "Prova final"
        assert props.reservation_data is None

    def test_from_occurrence_with_reservation_only(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(classroom=classroom)
        make_reservation(schedule=schedule)
        occurrence = make_occurrence(schedule=schedule)

        props = EventExtendedProps.from_occurrence(occurrence)

        assert props.reservation_data is not None
        assert props.reservation_data.occurrence_id == occurrence.id
        assert props.class_data is None

    def test_from_occurrence_with_neither(self) -> None:
        schedule = make_schedule()
        occurrence = make_occurrence(schedule=schedule)

        props = EventExtendedProps.from_occurrence(occurrence)

        assert props.class_data is None
        assert props.reservation_data is None

    def test_from_schedule_with_class_and_reservation(self) -> None:
        subject = make_subject()
        class_ = make_class(subject=subject)
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(class_=class_, classroom=classroom)
        make_reservation(schedule=schedule)

        props = EventExtendedProps.from_schedule(schedule)

        assert props.class_data is not None
        assert props.reservation_data is not None


class TestAllocationEventResponseHelpers:
    @pytest.mark.parametrize(
        ("reservation_type", "expected_prefix"),
        [
            (ReservationType.EVENT, "📅"),
            (ReservationType.MEETING, "👥"),
            (ReservationType.EXAM, "📝"),
        ],
    )
    def test_get_reservation_title_adds_an_emoji_per_type(
        self, reservation_type: ReservationType, expected_prefix: str
    ) -> None:
        schedule = make_schedule()
        reservation = make_reservation(
            schedule=schedule, type_=reservation_type, title="Título"
        )
        title = AllocationEventResponse.get_reservation_title(reservation)
        assert title == f"{expected_prefix} Título"

    def test_background_color_from_schedule_with_reservation(self) -> None:
        schedule = make_schedule()
        make_reservation(schedule=schedule, type_=ReservationType.EVENT)
        color = AllocationEventResponse.backgroundColor_from_schedule(schedule)
        assert color == ReservationType.get_color(ReservationType.EVENT)

    def test_background_color_from_schedule_without_reservation(self) -> None:
        schedule = make_schedule()
        schedule.reservation = None
        color = AllocationEventResponse.backgroundColor_from_schedule(schedule)
        assert color == "#408080"

    def test_type_from_schedule_with_reservation(self) -> None:
        schedule = make_schedule()
        make_reservation(schedule=schedule, type_=ReservationType.MEETING)
        assert (
            AllocationEventResponse.type_from_schedule(schedule)
            == AllocationEventType.MEETING
        )

    def test_type_from_schedule_without_reservation_is_subject(self) -> None:
        schedule = make_schedule()
        schedule.reservation = None
        assert (
            AllocationEventResponse.type_from_schedule(schedule)
            == AllocationEventType.SUBJECT
        )

    def test_get_class_title(self) -> None:
        subject = make_subject(code="MAC0110")
        class_ = make_class(subject=subject)
        assert AllocationEventResponse.get_class_title(class_) == "📚 MAC0110"


class TestAllocationEventResponseFromOccurrence:
    def test_with_an_allocated_classroom_and_class(self) -> None:
        building = make_building()
        classroom = make_classroom(building=building, name="Sala 9")
        subject = make_subject(code="MAC0110")
        class_ = make_class(subject=subject)
        schedule = make_schedule(class_=class_, classroom=classroom)
        occurrence = make_occurrence(schedule=schedule, classroom=classroom)

        event = AllocationEventResponse.from_occurrence(occurrence)

        assert event.id == str(occurrence.id)
        assert event.title == "📚 MAC0110"
        assert event.classroom == "Sala 9"
        assert event.resourceId == f"{building.name}-Sala 9"
        assert event.type == AllocationEventType.SUBJECT

    def test_without_a_classroom_uses_unallocated_resource_id(self) -> None:
        schedule = make_schedule(classroom=None)
        occurrence = make_occurrence(schedule=schedule, classroom=None)

        event = AllocationEventResponse.from_occurrence(occurrence)

        assert event.classroom is None
        assert event.resourceId == (
            f"{AllocationEnum.UNALLOCATED_BUILDING_ID.value}-"
            f"{AllocationEnum.UNALLOCATED_CLASSROOM_ID.value}"
        )

    def test_with_a_reservation_uses_the_reservation_title(self) -> None:
        classroom = make_classroom(building=make_building())
        schedule = make_schedule(classroom=classroom)
        make_reservation(schedule=schedule, type_=ReservationType.EVENT, title="Palestra")
        occurrence = make_occurrence(schedule=schedule)

        event = AllocationEventResponse.from_occurrence(occurrence)

        assert event.title == "📅 Palestra"
        assert event.type == AllocationEventType.EVENT


class TestAllocationEventResponseFromSchedule:
    def test_non_custom_recurrence_returns_a_single_event_with_rrule(self) -> None:
        building = make_building()
        classroom = make_classroom(building=building)
        subject = make_subject()
        class_ = make_class(subject=subject)
        schedule = make_schedule(
            class_=class_, classroom=classroom, recurrence=Recurrence.WEEKLY
        )

        events = AllocationEventResponse.from_schedule(schedule)

        assert len(events) == 1
        assert events[0].rrule is not None
        assert events[0].resourceId == f"{building.name}-{classroom.name}"

    def test_custom_recurrence_delegates_to_occurrences(self) -> None:
        schedule = make_schedule(recurrence=Recurrence.CUSTOM)
        occurrence1 = make_occurrence(
            schedule=schedule, occurrence_date=date(2025, 1, 6)
        )
        occurrence2 = make_occurrence(
            schedule=schedule, occurrence_date=date(2025, 1, 13)
        )
        schedule.occurrences = [occurrence1, occurrence2]

        events = AllocationEventResponse.from_schedule(schedule)

        assert [e.id for e in events] == [str(occurrence1.id), str(occurrence2.id)]
        assert all(e.rrule is None for e in events)


class TestAllocationResourceResponse:
    def test_from_building_includes_non_remote_classrooms_only(self) -> None:
        building = make_building(name="Bloco B")
        visible = make_classroom(building=building, name="Sala 1", remote=False)
        remote = make_classroom(building=building, name="Sala Remota", remote=True)
        building.classrooms = [visible, remote]

        resources = AllocationResourceResponse.from_building(building)

        ids = [r.id for r in resources]
        assert "Bloco B" in ids
        assert "Bloco B-Sala 1" in ids
        assert "Bloco B-Sala Remota" not in ids

    def test_from_classroom_sets_parent_id_to_the_building_name(self) -> None:
        building = make_building(name="Bloco C")
        classroom = make_classroom(building=building, name="Sala 2")

        resource = AllocationResourceResponse.from_classroom(classroom)

        assert resource.id == "Bloco C-Sala 2"
        assert resource.parentId == "Bloco C"
        assert resource.title == "Sala 2"

    def test_unnallocated_building_and_classroom_sentinels(self) -> None:
        building_sentinel = AllocationResourceResponse.unnallocated_building()
        classroom_sentinel = AllocationResourceResponse.unnallocated_classroom()

        assert building_sentinel.title == AllocationEnum.UNALLOCATED.value
        assert classroom_sentinel.parentId == building_sentinel.id
