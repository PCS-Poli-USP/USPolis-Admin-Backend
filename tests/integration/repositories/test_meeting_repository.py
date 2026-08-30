from datetime import date

import pytest
from sqlmodel import Session

from server.deps.interval_dep import QueryInterval
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.repositories.meeting_repository import MeetingNotFound, MeetingRepository
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.request.meeting_request_factory import MeetingRequestFactory
from tests.utils.validators.meeting.meeting_model_validator import MeetingModelAsserts


class TestCreate:
    def test_creates_a_meeting_with_a_classroom_and_allocates_it(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        input = MeetingRequestFactory(classroom=classroom).create_input()

        meeting = MeetingRepository.create(
            creator=admin_user, input=input, session=session
        )
        session.commit()
        session.refresh(meeting)

        MeetingModelAsserts.assert_meeting_after_create(meeting, input)
        assert meeting.reservation.schedule.classroom_id == classroom.id
        assert meeting.reservation.schedule.allocated is True

    def test_allocate_false_leaves_the_reservation_pending_and_unallocated(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        input = MeetingRequestFactory(classroom=classroom).create_input()

        meeting = MeetingRepository.create(
            creator=admin_user, input=input, session=session, allocate=False
        )
        session.commit()
        session.refresh(meeting)

        assert meeting.reservation.status == ReservationStatus.PENDING
        assert meeting.reservation.schedule.allocated is False


class TestGetById:
    def test_returns_the_matching_meeting(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        input = MeetingRequestFactory(classroom=classroom).create_input()
        created = MeetingRepository.create(
            creator=admin_user, input=input, session=session
        )
        session.commit()

        found = MeetingRepository.get_by_id(id=must_be_int(created.id), session=session)

        assert found.id == created.id

    def test_raises_when_meeting_does_not_exist(self, session: Session) -> None:
        with pytest.raises(MeetingNotFound):
            MeetingRepository.get_by_id(id=999999, session=session)


class TestGetAll:
    def test_returns_meetings_active_today_by_default(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        input = MeetingRequestFactory(classroom=classroom).create_input()
        meeting = MeetingRepository.create(
            creator=admin_user, input=input, session=session
        )
        session.commit()

        meetings = MeetingRepository.get_all(session=session, interval=QueryInterval())

        assert meeting.id in [m.id for m in meetings]

    def test_excludes_meetings_outside_the_start_end_interval(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        input = MeetingRequestFactory(classroom=classroom).create_input()
        meeting = MeetingRepository.create(
            creator=admin_user, input=input, session=session
        )
        session.commit()

        meetings = MeetingRepository.get_all(
            session=session,
            interval=QueryInterval(start=date(1999, 1, 1), end=date(1999, 12, 31)),
        )

        assert meeting.id not in [m.id for m in meetings]


class TestUpdate:
    def test_updates_the_link(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        create_input = MeetingRequestFactory(classroom=classroom).create_input()
        meeting = MeetingRepository.create(
            creator=admin_user, input=create_input, session=session
        )
        session.commit()

        update_input = MeetingRequestFactory(classroom=classroom).update_input(
            link="https://updated.example.com"
        )

        updated = MeetingRepository.update(
            id=must_be_int(meeting.id),
            user=admin_user,
            input=update_input,
            session=session,
        )
        session.commit()
        session.refresh(updated)

        MeetingModelAsserts.assert_meeting_after_update(updated, update_input)

    def test_raises_when_meeting_does_not_exist(
        self, admin_user: User, classroom: Classroom, session: Session
    ) -> None:
        update_input = MeetingRequestFactory(classroom=classroom).update_input()

        with pytest.raises(MeetingNotFound):
            MeetingRepository.update(
                id=999999, user=admin_user, input=update_input, session=session
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

        create_input = MeetingRequestFactory(classroom=classroom).create_input()
        meeting = MeetingRepository.create(
            creator=admin_user, input=create_input, session=session
        )
        session.commit()

        update_input = MeetingRequestFactory(classroom=other_classroom).update_input()
        updated = MeetingRepository.update(
            id=must_be_int(meeting.id),
            user=admin_user,
            input=update_input,
            session=session,
        )
        session.commit()
        session.refresh(updated)

        assert updated.reservation.schedule.classroom_id == other_classroom.id
