from datetime import date

import pytest
from sqlmodel import Session

from server.deps.interval_dep import QueryInterval
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.repositories.event_repository import EventNotFound, EventRepository
from server.utils.enums.event_type_enum import EventType
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.request.event_request_factory import EventRequestFactory
from tests.utils.validators.event.event_model_validator import EventModelAsserts


class TestCreate:
    def test_creates_an_event_with_a_classroom_and_allocates_it(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        input = EventRequestFactory(classroom=classroom).create_input()

        event = EventRepository.create(creator=admin_user, input=input, session=session)
        session.commit()
        session.refresh(event)

        EventModelAsserts.assert_event_after_create(event, input)
        assert event.reservation.schedule.classroom_id == classroom.id
        assert event.reservation.schedule.allocated is True

    def test_allocate_false_leaves_the_reservation_pending_and_unallocated(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        input = EventRequestFactory(classroom=classroom).create_input()

        event = EventRepository.create(
            creator=admin_user, input=input, session=session, allocate=False
        )
        session.commit()
        session.refresh(event)

        assert event.reservation.status == ReservationStatus.PENDING
        assert event.reservation.schedule.allocated is False


class TestGetById:
    def test_returns_the_matching_event(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        input = EventRequestFactory(classroom=classroom).create_input()
        created = EventRepository.create(
            creator=admin_user, input=input, session=session
        )
        session.commit()

        found = EventRepository.get_by_id(id=must_be_int(created.id), session=session)

        assert found.id == created.id

    def test_raises_when_event_does_not_exist(self, session: Session) -> None:
        with pytest.raises(EventNotFound):
            EventRepository.get_by_id(id=999999, session=session)


class TestGetAll:
    def test_returns_events_active_today_by_default(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        input = EventRequestFactory(classroom=classroom).create_input()
        event = EventRepository.create(creator=admin_user, input=input, session=session)
        session.commit()

        events = EventRepository.get_all(session=session, interval=QueryInterval())

        assert event.id in [e.id for e in events]

    def test_excludes_events_outside_the_start_end_interval(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        input = EventRequestFactory(classroom=classroom).create_input()
        event = EventRepository.create(creator=admin_user, input=input, session=session)
        session.commit()

        events = EventRepository.get_all(
            session=session,
            interval=QueryInterval(start=date(1999, 1, 1), end=date(1999, 12, 31)),
        )

        assert event.id not in [e.id for e in events]


class TestUpdate:
    def test_updates_link_and_type(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        create_input = EventRequestFactory(classroom=classroom).create_input()
        event = EventRepository.create(
            creator=admin_user, input=create_input, session=session
        )
        session.commit()

        factory = EventRequestFactory(classroom=classroom)
        update_input = factory.update_input(
            link="https://updated.example.com", event_type=EventType.WORKSHOP
        )

        updated = EventRepository.update(
            user=admin_user,
            id=must_be_int(event.id),
            input=update_input,
            session=session,
        )
        session.commit()
        session.refresh(updated)

        EventModelAsserts.assert_event_after_update(updated, update_input)

    def test_raises_when_event_does_not_exist(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        update_input = EventRequestFactory(classroom=classroom).update_input()

        with pytest.raises(EventNotFound):
            EventRepository.update(
                user=admin_user, id=999999, input=update_input, session=session
            )

    def test_moving_to_a_different_classroom_reallocates(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        other_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()

        create_input = EventRequestFactory(classroom=classroom).create_input()
        event = EventRepository.create(
            creator=admin_user, input=create_input, session=session
        )
        session.commit()

        update_input = EventRequestFactory(classroom=other_classroom).update_input()
        updated = EventRepository.update(
            user=admin_user,
            id=must_be_int(event.id),
            input=update_input,
            session=session,
        )
        session.commit()
        session.refresh(updated)

        assert updated.reservation.schedule.classroom_id == other_classroom.id
