from datetime import date, timedelta

import pytest
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.models.http.requests.schedule_request_models import (
    ScheduleUpdateOccurrences,
)
from server.repositories.schedule_repository import (
    InvalidScheduleAllocationReuseTarget,
    ScheduleNotFound,
    ScheduleRepository,
)
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.recurrence import Recurrence
from server.utils.enums.reservation_type import ReservationType
from server.utils.enums.week_day import WeekDay
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.class_model_factory import ClassModelFactory
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.occurrence_model_factory import OccurrenceModelFactory
from tests.factories.model.reservation_model_factory import ReservationModelFactory
from tests.factories.model.schedule_model_factory import ScheduleModelFactory
from tests.factories.request.schedule_request_factory import ScheduleRequestFactory


def _make_reservation_with_classroom(
    *, creator: User, classroom: Classroom, session: Session
) -> Reservation:
    reservation = ReservationModelFactory(
        reservation_type=ReservationType.MEETING,
        creator=creator,
        classroom=classroom,
        session=session,
    ).create_and_refresh()
    # ReservationModelFactory never wires the given classroom onto the
    # schedule it auto-creates - link it manually.
    reservation.schedule.classroom = classroom
    session.add(reservation.schedule)
    session.commit()
    session.refresh(reservation)
    return reservation


class TestGetAll:
    def test_returns_every_schedule(self, class_: Class, session: Session) -> None:
        schedule = class_.schedules[0]

        schedules = ScheduleRepository.get_all(session=session)

        assert schedule.id in [s.id for s in schedules]


class TestGetById:
    def test_returns_the_matching_schedule(
        self, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]

        found = ScheduleRepository.get_by_id(id=must_be_int(schedule.id), session=session)

        assert found.id == schedule.id

    def test_raises_when_schedule_does_not_exist(self, session: Session) -> None:
        with pytest.raises(ScheduleNotFound):
            ScheduleRepository.get_by_id(id=999999, session=session)


class TestGetByIds:
    def test_returns_only_the_matching_schedules(
        self, subject: Subject, class_: Class, session: Session
    ) -> None:
        other_class = ClassModelFactory(
            subject=subject, session=session
        ).create_and_refresh()
        schedule = class_.schedules[0]
        other_schedule = other_class.schedules[0]

        found = ScheduleRepository.get_by_ids(
            ids=[must_be_int(schedule.id), must_be_int(other_schedule.id)],
            session=session,
        )

        assert {s.id for s in found} == {schedule.id, other_schedule.id}


class TestGetAllUnallocatedForClasses:
    def test_returns_unallocated_non_custom_class_schedules(
        self, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]

        schedules = ScheduleRepository.get_all_unallocated_for_classes(session=session)

        assert schedule.id in [s.id for s in schedules]

    def test_excludes_allocated_schedules(
        self, allocated_classroom: Classroom, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]

        schedules = ScheduleRepository.get_all_unallocated_for_classes(session=session)

        assert schedule.id not in [s.id for s in schedules]

    def test_excludes_reservation_schedules(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _make_reservation_with_classroom(
            creator=admin_user, classroom=classroom, session=session
        )

        schedules = ScheduleRepository.get_all_unallocated_for_classes(session=session)

        assert reservation.schedule.id not in [s.id for s in schedules]


class TestGetAllOnClass:
    def test_returns_schedules_of_the_given_class(
        self, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]

        schedules = ScheduleRepository.get_all_on_class(class_=class_, session=session)

        assert [s.id for s in schedules] == [schedule.id]


class TestGetByIdOnClass:
    def test_returns_the_matching_schedule(
        self, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]

        found = ScheduleRepository.get_by_id_on_class(
            class_=class_, id=must_be_int(schedule.id), session=session
        )

        assert found.id == schedule.id

    def test_raises_when_schedule_does_not_belong_to_the_class(
        self, subject: Subject, class_: Class, session: Session
    ) -> None:
        other_class = ClassModelFactory(
            subject=subject, session=session
        ).create_and_refresh()

        with pytest.raises(ScheduleNotFound):
            ScheduleRepository.get_by_id_on_class(
                class_=class_,
                id=must_be_int(other_class.schedules[0].id),
                session=session,
            )


class TestGetByIdOnBuildings:
    def test_class_based_schedule_matches_its_subjects_building(
        self, building: Building, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]

        found = ScheduleRepository.get_by_id_on_buildings(
            schedule_id=must_be_int(schedule.id),
            owned_building_ids=[must_be_int(building.id)],
            session=session,
        )

        assert found.id == schedule.id

    def test_raises_when_class_based_schedule_building_does_not_match(
        self, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]

        with pytest.raises(ScheduleNotFound):
            ScheduleRepository.get_by_id_on_buildings(
                schedule_id=must_be_int(schedule.id),
                owned_building_ids=[999999],
                session=session,
            )

    def test_reservation_based_schedule_matches_its_building(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        reservation = _make_reservation_with_classroom(
            creator=admin_user, classroom=classroom, session=session
        )

        found = ScheduleRepository.get_by_id_on_buildings(
            schedule_id=must_be_int(reservation.schedule.id),
            owned_building_ids=[must_be_int(building.id)],
            session=session,
        )

        assert found.id == reservation.schedule.id

    def test_raises_when_reservation_based_schedule_building_does_not_match(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _make_reservation_with_classroom(
            creator=admin_user, classroom=classroom, session=session
        )

        with pytest.raises(ScheduleNotFound):
            ScheduleRepository.get_by_id_on_buildings(
                schedule_id=must_be_int(reservation.schedule.id),
                owned_building_ids=[999999],
                session=session,
            )


class TestGetCommingClassSchedules:
    def test_returns_schedules_with_an_occurrence_in_the_next_two_days(
        self, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        OccurrenceModelFactory(schedule=schedule, session=session).create_and_refresh(
            date=BrazilDatetime.now_utc().date() + timedelta(days=1)
        )

        schedules = ScheduleRepository.get_comming_class_schedules(session=session)

        assert schedule.id in [s.id for s in schedules]

    def test_excludes_schedules_without_an_upcoming_occurrence(
        self, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        OccurrenceModelFactory(schedule=schedule, session=session).create_and_refresh(
            date=date(2000, 1, 1)
        )

        schedules = ScheduleRepository.get_comming_class_schedules(session=session)

        assert schedule.id not in [s.id for s in schedules]


def _make_matching_schedule(
    *, target: Schedule, subject: Subject, classroom: Classroom, session: Session
) -> Schedule:
    other_class = ClassModelFactory(
        subject=subject, session=session
    ).create_and_refresh(schedules=[])
    schedule = ScheduleModelFactory(session=session).create_and_refresh(
        class_id=must_be_int(other_class.id),
        week_day=target.week_day,
        month_week=target.month_week,
        recurrence=target.recurrence,
        start_date=target.start_date,
        end_date=target.end_date,
        start_time=target.start_time,
        end_time=target.end_time,
        # Both the FK id and the relationship object must be overridden
        # together - SQLAlchemy resyncs classroom_id from the `classroom`
        # relationship's value at flush time, so setting only classroom_id
        # gets silently clobbered back to None.
        classroom_id=must_be_int(classroom.id),
        classroom=classroom,
    )
    other_class.schedules = [schedule]
    session.add(other_class)
    session.commit()
    session.refresh(schedule)
    return schedule


class TestFindOldAllocationOptions:
    def test_raises_when_target_has_no_class(self, session: Session) -> None:
        target = ScheduleModelFactory(session=session).create_and_refresh()

        with pytest.raises(InvalidScheduleAllocationReuseTarget):
            ScheduleRepository.find_old_allocation_options(
                building_id=1, year=2025, target=target, session=session
            )

    def test_finds_a_matching_schedule_for_the_same_subject_in_the_building(
        self,
        building: Building,
        classroom: Classroom,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        target = ScheduleModelFactory(session=session).create_and_refresh(
            class_id=must_be_int(class_.id),
            week_day=WeekDay.MONDAY,
            month_week=None,
            recurrence=Recurrence.WEEKLY,
            # Kept within a single calendar year - find_old_allocation_options
            # scopes its search to [Jan 1, Dec 31] of `year`, which a
            # semester's real (Faker-generated) date range can straddle.
            start_date=date(2025, 3, 1),
            end_date=date(2025, 7, 1),
        )
        class_.schedules = [target]
        session.add(class_)
        session.commit()
        session.refresh(target)

        old_schedule = _make_matching_schedule(
            target=target, subject=subject, classroom=classroom, session=session
        )

        options = ScheduleRepository.find_old_allocation_options(
            building_id=must_be_int(building.id),
            year=target.start_date.year,
            target=target,
            session=session,
        )

        assert old_schedule.id in [s.id for s in options]

    def test_excludes_options_in_a_different_building(
        self,
        admin_user: User,
        building: Building,
        subject: Subject,
        class_: Class,
        session: Session,
    ) -> None:
        other_building = BuildingModelFactory(admin_user, session).create_and_refresh()
        other_classroom = ClassroomModelFactory(
            creator=admin_user, building=other_building, session=session
        ).create_and_refresh()

        target = ScheduleModelFactory(session=session).create_and_refresh(
            class_id=must_be_int(class_.id),
            week_day=WeekDay.MONDAY,
            month_week=None,
            recurrence=Recurrence.WEEKLY,
            start_date=date(2025, 3, 1),
            end_date=date(2025, 7, 1),
        )
        class_.schedules = [target]
        session.add(class_)
        session.commit()
        session.refresh(target)

        old_schedule = _make_matching_schedule(
            target=target, subject=subject, classroom=other_classroom, session=session
        )

        options = ScheduleRepository.find_old_allocation_options(
            building_id=must_be_int(building.id),
            year=target.start_date.year,
            target=target,
            session=session,
        )

        assert old_schedule.id not in [s.id for s in options]


class TestCreateWithClass:
    def test_creates_a_schedule_linked_to_the_class(
        self, class_: Class, session: Session
    ) -> None:
        input = ScheduleRequestFactory().create_input()

        schedule = ScheduleRepository.create_with_class(
            class_=class_, input=input, session=session
        )
        session.commit()
        session.refresh(schedule)

        assert schedule.class_id == class_.id
        assert schedule.classroom_id is None

    def test_creates_occurrences_for_a_custom_recurrence_with_dates(
        self, class_: Class, session: Session
    ) -> None:
        factory = ScheduleRequestFactory()
        dates = factory.get_random_dates(date(2025, 3, 1), date(2025, 3, 10), 2)
        input = factory.create_input(
            recurrence=Recurrence.CUSTOM, week_day=None, dates=dates
        )

        schedule = ScheduleRepository.create_with_class(
            class_=class_, input=input, session=session
        )
        session.commit()
        session.refresh(schedule)

        assert {o.date for o in schedule.occurrences} == set(dates)


class TestCreateWithReservation:
    def test_allocate_true_with_a_classroom_allocates_the_schedule(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = ReservationModelFactory(
            reservation_type=ReservationType.MEETING,
            creator=admin_user,
            classroom=classroom,
            session=session,
        ).create_and_refresh(schedule=None)  # type: ignore[arg-type]
        input = ScheduleRequestFactory(classroom=classroom).create_input()

        schedule = ScheduleRepository.create_with_reservation(
            user=admin_user,
            reservation=reservation,
            input=input,
            classroom=classroom,
            session=session,
        )
        session.commit()
        session.refresh(schedule)

        assert schedule.allocated is True
        assert schedule.classroom_id == classroom.id

    def test_allocate_false_leaves_the_schedule_unallocated(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = ReservationModelFactory(
            reservation_type=ReservationType.MEETING,
            creator=admin_user,
            classroom=classroom,
            session=session,
        ).create_and_refresh(schedule=None)  # type: ignore[arg-type]
        input = ScheduleRequestFactory(classroom=classroom).create_input()

        schedule = ScheduleRepository.create_with_reservation(
            user=admin_user,
            reservation=reservation,
            input=input,
            classroom=classroom,
            session=session,
            allocate=False,
        )
        session.commit()
        session.refresh(schedule)

        assert schedule.allocated is False


class TestDuplicate:
    def test_copies_core_fields_without_allocation(
        self, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]

        duplicate = ScheduleRepository.duplicate(schedule=schedule, session=session)
        session.commit()
        session.refresh(duplicate)

        assert duplicate.id != schedule.id
        assert duplicate.start_date == schedule.start_date
        assert duplicate.recurrence == schedule.recurrence
        assert duplicate.allocated is False
        assert duplicate.class_id is None


class TestCreateManyWithClass:
    def test_creates_one_schedule_per_input(
        self, class_: Class, session: Session
    ) -> None:
        factory = ScheduleRequestFactory()
        inputs = [factory.create_input(), factory.create_input()]

        schedules = ScheduleRepository.create_many_with_class(
            class_=class_, input=inputs, session=session
        )
        session.commit()

        assert len(schedules) == 2
        assert all(s.class_id == class_.id for s in schedules)


class TestUpdateClassSchedules:
    def test_replaces_existing_schedules(
        self, admin_user: User, class_: Class, session: Session
    ) -> None:
        old_schedule_id = must_be_int(class_.schedules[0].id)
        factory = ScheduleRequestFactory()
        new_input = [factory.update_input()]

        updated = ScheduleRepository.update_class_schedules(
            class_=class_, user=admin_user, input=new_input, session=session
        )
        session.commit()

        assert len(updated) == 1
        assert updated[0].id != old_schedule_id
        assert (
            ScheduleRepository.get_by_ids(ids=[old_schedule_id], session=session) == []
        )

    def test_allocates_when_the_input_requests_it(
        self, admin_user: User, classroom: Classroom, class_: Class, session: Session
    ) -> None:
        factory = ScheduleRequestFactory(classroom=classroom)
        new_input = [
            factory.update_input(
                allocated=True, classroom_id=must_be_int(classroom.id)
            )
        ]

        updated = ScheduleRepository.update_class_schedules(
            class_=class_, user=admin_user, input=new_input, session=session
        )
        session.commit()
        session.refresh(updated[0])

        assert updated[0].allocated is True
        assert updated[0].classroom_id == classroom.id


class TestUpdateReservationSchedule:
    def test_keeps_the_same_schedule_when_nothing_changed(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        reservation = _make_reservation_with_classroom(
            creator=admin_user, classroom=classroom, session=session
        )
        old_schedule = reservation.schedule
        update_input = ScheduleRequestFactory(classroom=classroom).update_input(
            start_date=old_schedule.start_date,
            end_date=old_schedule.end_date,
            start_time=old_schedule.start_time,
            end_time=old_schedule.end_time,
            recurrence=old_schedule.recurrence,
            week_day=old_schedule.week_day,
            month_week=old_schedule.month_week,
            all_day=old_schedule.all_day,
            allocated=old_schedule.allocated,
            classroom_id=must_be_int(classroom.id),
        )

        result = ScheduleRepository.update_reservation_schedule(
            user=admin_user,
            reservation=reservation,
            input=update_input,
            classroom=classroom,
            session=session,
        )

        assert result.id == old_schedule.id

    def test_reallocates_when_the_classroom_changes(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        other_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        reservation = _make_reservation_with_classroom(
            creator=admin_user, classroom=classroom, session=session
        )
        old_schedule_id = must_be_int(reservation.schedule.id)
        update_input = ScheduleRequestFactory(classroom=other_classroom).update_input()

        result = ScheduleRepository.update_reservation_schedule(
            user=admin_user,
            reservation=reservation,
            input=update_input,
            classroom=other_classroom,
            session=session,
        )
        session.commit()
        session.refresh(result)

        assert result.id != old_schedule_id
        assert result.classroom_id == other_classroom.id


class TestUpdateOccurrences:
    def test_adds_and_removes_occurrences_and_updates_the_date_range(
        self, class_: Class, session: Session
    ) -> None:
        schedule = class_.schedules[0]
        kept_date = date(2025, 4, 1)
        removed_occurrence = OccurrenceModelFactory(
            schedule=schedule, session=session
        ).create_and_refresh(date=date(2025, 1, 1))
        OccurrenceModelFactory(schedule=schedule, session=session).create_and_refresh(
            date=kept_date
        )
        session.commit()
        session.refresh(schedule)

        added_date = date(2025, 5, 1)
        updated = ScheduleRepository.update_occurrences(
            id=must_be_int(schedule.id),
            input=ScheduleUpdateOccurrences(dates=[kept_date, added_date]),
            session=session,
        )
        session.commit()
        session.refresh(updated)

        occurrence_dates = {o.date for o in updated.occurrences}
        assert occurrence_dates == {kept_date, added_date}
        assert removed_occurrence.date not in occurrence_dates
        assert updated.start_date == kept_date
        assert updated.end_date == added_date


class TestDelete:
    def test_deletes_the_schedule(self, class_: Class, session: Session) -> None:
        schedule_id = must_be_int(class_.schedules[0].id)

        ScheduleRepository.delete(id=schedule_id, session=session)
        session.commit()

        with pytest.raises(ScheduleNotFound):
            ScheduleRepository.get_by_id(id=schedule_id, session=session)

    def test_raises_when_schedule_does_not_exist(self, session: Session) -> None:
        with pytest.raises(ScheduleNotFound):
            ScheduleRepository.delete(id=999999, session=session)
