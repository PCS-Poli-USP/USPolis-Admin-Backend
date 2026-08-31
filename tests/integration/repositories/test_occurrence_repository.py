from datetime import date, time, timedelta

from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.http.requests.occurrence_request_models import (
    OccurenceManyRegister,
    OccurrenceRegister,
)
from server.repositories.occurrence_repository import OccurrenceRepository
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.occurrence_model_factory import OccurrenceModelFactory


class TestGetById:
    def test_returns_the_matching_occurrence(
        self, class_: Class, session: Session
    ) -> None:
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session
        ).create_and_refresh()

        found = OccurrenceRepository.get_by_id(id=must_be_int(occurrence.id), session=session)

        assert found.id == occurrence.id


class TestGetByIds:
    def test_returns_only_the_matching_occurrences_ordered_by_date(
        self, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        later = OccurrenceModelFactory(
            schedule=schedule, session=session
        ).create_and_refresh(date=date(2025, 6, 1))
        earlier = OccurrenceModelFactory(
            schedule=schedule, session=session
        ).create_and_refresh(date=date(2025, 1, 1))

        found = OccurrenceRepository.get_by_ids(
            ids=[must_be_int(later.id), must_be_int(earlier.id)], session=session
        )

        assert [o.id for o in found] == [earlier.id, later.id]


class TestGetByDateAndClassroom:
    def test_returns_occurrences_on_the_given_date_and_classroom(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))

        found = OccurrenceRepository.get_by_date_and_classroom(
            date=date(2025, 3, 1), classroom_id=must_be_int(classroom.id), session=session
        )

        assert [o.id for o in found] == [occurrence.id]

    def test_excludes_occurrences_on_a_different_date(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 1))

        found = OccurrenceRepository.get_by_date_and_classroom(
            date=date(2025, 4, 1), classroom_id=must_be_int(classroom.id), session=session
        )

        assert found == []


class TestGetAllOnBuildings:
    def test_returns_occurrences_of_classrooms_in_the_given_building(
        self, building: Building, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=classroom
        ).create_and_refresh()

        found = OccurrenceRepository.get_all_on_buildings(
            building_ids=[must_be_int(building.id)], session=session
        )

        assert occurrence.id in [o.id for o in found]

    def test_excludes_occurrences_of_other_buildings(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=classroom
        ).create_and_refresh()

        found = OccurrenceRepository.get_all_on_buildings(
            building_ids=[999999], session=session
        )

        assert occurrence.id not in [o.id for o in found]


class TestGetAllOnInterval:
    def test_returns_occurrences_within_the_interval(
        self, class_: Class, session: Session
    ) -> None:
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session
        ).create_and_refresh(date=date(2025, 3, 15))

        found = OccurrenceRepository.get_all_on_interval(
            start=date(2025, 3, 1), end=date(2025, 3, 31), session=session
        )

        assert occurrence.id in [o.id for o in found]

    def test_excludes_occurrences_outside_the_interval(
        self, class_: Class, session: Session
    ) -> None:
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session
        ).create_and_refresh(date=date(2025, 3, 15))

        found = OccurrenceRepository.get_all_on_interval(
            start=date(1999, 1, 1), end=date(1999, 12, 31), session=session
        )

        assert occurrence.id not in [o.id for o in found]


class TestGetAllOnIntervalForAllocation:
    def test_includes_a_non_remote_allocated_occurrence(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        classroom.remote = False
        session.add(classroom)
        session.commit()
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 15))

        found = OccurrenceRepository.get_all_on_interval_for_allocation(
            start=date(2025, 3, 1), end=date(2025, 3, 31), session=session
        )

        assert occurrence.id in [o.id for o in found]

    def test_includes_an_unallocated_class_occurrence(
        self, class_: Class, session: Session
    ) -> None:
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=None
        ).create_and_refresh(date=date(2025, 3, 15))

        found = OccurrenceRepository.get_all_on_interval_for_allocation(
            start=date(2025, 3, 1), end=date(2025, 3, 31), session=session
        )

        assert occurrence.id in [o.id for o in found]

    def test_excludes_a_remote_allocated_occurrence(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        classroom.remote = True
        session.add(classroom)
        session.commit()
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 15))

        found = OccurrenceRepository.get_all_on_interval_for_allocation(
            start=date(2025, 3, 1), end=date(2025, 3, 31), session=session
        )

        assert occurrence.id not in [o.id for o in found]


class TestGetAllOnIntervalForClassroom:
    def test_returns_occurrences_of_the_given_classroom_within_the_interval(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 15))

        found = OccurrenceRepository.get_all_on_interval_for_classroom(
            classroom_id=must_be_int(classroom.id),
            start=date(2025, 3, 1),
            end=date(2025, 3, 31),
            session=session,
        )

        assert [o.id for o in found] == [occurrence.id]

    def test_excludes_occurrences_of_other_classrooms(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=classroom
        ).create_and_refresh(date=date(2025, 3, 15))

        found = OccurrenceRepository.get_all_on_interval_for_classroom(
            classroom_id=999999,
            start=date(2025, 3, 1),
            end=date(2025, 3, 31),
            session=session,
        )

        assert found == []


class TestGetAllOnIntervalForNow:
    def test_returns_occurrences_from_today_onward(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=classroom
        ).create_and_refresh(date=date.today() + timedelta(days=1))

        found = OccurrenceRepository.get_all_on_interval_for_now(
            classroom_id=must_be_int(classroom.id), session=session
        )

        assert [o.id for o in found] == [occurrence.id]

    def test_excludes_occurrences_in_the_past(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=classroom
        ).create_and_refresh(date=date(2000, 1, 1))

        found = OccurrenceRepository.get_all_on_interval_for_now(
            classroom_id=must_be_int(classroom.id), session=session
        )

        assert found == []


class TestAllocateOccurrence:
    def test_sets_the_classroom_on_the_occurrence(
        self, admin_user: User, building: Building, class_: Class, session: Session
    ) -> None:
        other_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=None
        ).create_and_refresh()

        OccurrenceRepository.allocate_occurrence(
            occurrence=occurrence, classroom=other_classroom, session=session
        )
        session.commit()
        session.refresh(occurrence)

        assert occurrence.classroom_id == other_classroom.id


class TestAllocateSchedule:
    def test_generates_and_allocates_occurrences_and_logs_the_action(
        self, admin_user: User, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]

        occurrences = OccurrenceRepository.allocate_schedule(
            user=admin_user, schedule=schedule, classroom=classroom, session=session
        )
        session.commit()
        session.refresh(schedule)

        assert len(occurrences) > 0
        assert schedule.allocated is True
        assert schedule.classroom_id == classroom.id
        assert all(o.classroom_id == classroom.id for o in schedule.occurrences)
        assert len(schedule.logs) == 1


class TestRemoveOccurrenceAllocation:
    def test_clears_the_classroom(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        occurrence = OccurrenceModelFactory(
            schedule=class_.schedules[0], session=session, classroom=classroom
        ).create_and_refresh()

        OccurrenceRepository.remove_occurrence_allocation(
            occurrence=occurrence, session=session
        )
        session.commit()
        session.refresh(occurrence)

        assert occurrence.classroom_id is None


class TestRemoveScheduleAllocation:
    def test_clears_allocation_and_logs_the_deallocation(
        self, admin_user: User, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        OccurrenceRepository.allocate_schedule(
            user=admin_user, schedule=schedule, classroom=classroom, session=session
        )
        session.commit()
        session.refresh(schedule)

        OccurrenceRepository.remove_schedule_allocation(
            user=admin_user, schedule=schedule, session=session
        )
        session.commit()
        session.refresh(schedule)

        assert schedule.allocated is False
        assert schedule.classroom_id is None
        assert schedule.occurrences == []
        assert len(schedule.logs) == 2


class TestCreateWithSchedule:
    def test_creates_an_occurrence_linked_to_the_schedule_and_classroom(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        input = OccurrenceRegister(
            schedule_id=must_be_int(schedule.id),
            classroom_id=must_be_int(classroom.id),
            start_time=time(8, 0),
            end_time=time(10, 0),
            date=date(2025, 3, 1),
        )

        occurrence = OccurrenceRepository.create_with_schedule(
            schedule=schedule, input=input, session=session
        )

        assert occurrence.schedule_id == schedule.id
        assert occurrence.classroom_id == classroom.id
        assert occurrence.date == date(2025, 3, 1)


class TestCreateManyWithSchedule:
    def test_creates_one_occurrence_per_date(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        input = OccurenceManyRegister(
            classroom_id=must_be_int(classroom.id),
            start_time=time(8, 0),
            end_time=time(10, 0),
            dates=[date(2025, 3, 1), date(2025, 3, 8)],
        )

        occurrences = OccurrenceRepository.create_many_with_schedule(
            schedule=schedule, input=input, session=session
        )
        session.commit()

        assert {o.date for o in occurrences} == {date(2025, 3, 1), date(2025, 3, 8)}
        assert all(o.classroom_id == classroom.id for o in occurrences)

    def test_creates_labels_when_provided(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        input = OccurenceManyRegister(
            classroom_id=must_be_int(classroom.id),
            start_time=time(8, 0),
            end_time=time(10, 0),
            dates=[date(2025, 3, 1)],
            labels=["Prova final"],
        )

        occurrences = OccurrenceRepository.create_many_with_schedule(
            schedule=schedule, input=input, session=session
        )
        session.commit()
        session.refresh(occurrences[0])

        assert occurrences[0].occurrence_label is not None
        assert occurrences[0].occurrence_label.label == "Prova final"

    def test_uses_distinct_times_per_date_when_provided(
        self, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        input = OccurenceManyRegister(
            classroom_id=must_be_int(classroom.id),
            start_time=time(8, 0),
            end_time=time(10, 0),
            dates=[date(2025, 3, 1), date(2025, 3, 8)],
            times=[(time(9, 0), time(11, 0)), (time(14, 0), time(16, 0))],
        )

        occurrences = OccurrenceRepository.create_many_with_schedule(
            schedule=schedule, input=input, session=session
        )
        session.commit()

        occurrences.sort(key=lambda o: o.date)
        assert occurrences[0].start_time == time(9, 0)
        assert occurrences[1].start_time == time(14, 0)
