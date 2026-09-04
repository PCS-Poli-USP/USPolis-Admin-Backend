from datetime import date, timedelta

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.http.requests.solicitation_request_models import (
    EventSolicitation,
    MeetingSolicitation,
    SolicitationDeny,
    SolicitationRegister,
)
from server.models.page_models import PaginationInput
from server.repositories.solicitation_repository import (
    ClassroomNotReservable,
    SolicitationAlreadyClosed,
    SolicitationInvalidClassroom,
    SolicitationNotFound,
    SolicitationPermissionDenied,
    SolicitationRepository,
)
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.must_be_int import must_be_int
from tests.factories.model.building_model_factory import BuildingModelFactory
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.user_model_factory import UserModelFactory
from tests.factories.request.event_request_factory import EventRequestFactory
from tests.factories.request.meeting_request_factory import MeetingRequestFactory


def _meeting_solicitation_input(
    *,
    building: Building,
    schedule_classroom: Classroom,
    requested_classroom: Classroom | None,
    capacity: int = 10,
    required_classroom: bool = False,
) -> SolicitationRegister:
    base = MeetingRequestFactory(classroom=schedule_classroom).create_input()
    dump = base.model_dump()
    dump["classroom_id"] = requested_classroom.id if requested_classroom else None
    reservation_data = MeetingSolicitation(**dump)
    return SolicitationRegister(
        capacity=capacity,
        required_classroom=required_classroom,
        building_id=must_be_int(building.id),
        reservation_data=reservation_data,
    )


def _event_solicitation_input(
    *,
    building: Building,
    schedule_classroom: Classroom,
    requested_classroom: Classroom | None,
    capacity: int = 10,
    required_classroom: bool = False,
) -> SolicitationRegister:
    base = EventRequestFactory(classroom=schedule_classroom).create_input()
    dump = base.model_dump()
    dump["classroom_id"] = requested_classroom.id if requested_classroom else None
    reservation_data = EventSolicitation(**dump)
    return SolicitationRegister(
        capacity=capacity,
        required_classroom=required_classroom,
        building_id=must_be_int(building.id),
        reservation_data=reservation_data,
    )


def _make_unreservable(classroom: Classroom, session: Session) -> Classroom:
    # ClassroomBaseFactory doesn't expose `reservable` as an overridable key
    # (same gap as the `remote` field), so it's set directly here rather than
    # via the factory - see tests/utils/academic_test_utils.py's make_classroom
    # for the established precedent.
    classroom.reservable = False
    session.add(classroom)
    session.commit()
    session.refresh(classroom)
    return classroom


class TestCreate:
    def test_creates_a_meeting_solicitation_with_a_requested_classroom(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        input = _meeting_solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
        )

        solicitation = SolicitationRepository.create(
            requester=admin_user, input=input, session=session
        )
        session.commit()
        session.refresh(solicitation)

        assert solicitation.building_id == building.id
        assert solicitation.solicited_classroom_id == classroom.id
        assert solicitation.get_status() == ReservationStatus.PENDING
        assert solicitation.reservation.schedule.allocated is False

    def test_creates_a_solicitation_without_a_requested_classroom(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        input = _meeting_solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=None,
        )

        solicitation = SolicitationRepository.create(
            requester=admin_user, input=input, session=session
        )
        session.commit()
        session.refresh(solicitation)

        assert solicitation.solicited_classroom_id is None
        assert solicitation.solicited_classroom is None

    def test_creates_an_event_solicitation(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        input = _event_solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
        )

        solicitation = SolicitationRepository.create(
            requester=admin_user, input=input, session=session
        )
        session.commit()
        session.refresh(solicitation)

        assert solicitation.reservation.event is not None

    def test_raises_when_the_classroom_does_not_belong_to_the_building(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        other_building = BuildingModelFactory(admin_user, session).create_and_refresh()
        input = _meeting_solicitation_input(
            building=other_building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
        )

        with pytest.raises(SolicitationInvalidClassroom):
            SolicitationRepository.create(
                requester=admin_user, input=input, session=session
            )

    def test_raises_when_the_classroom_is_not_reservable(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        _make_unreservable(classroom, session)
        input = _meeting_solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
        )

        with pytest.raises(ClassroomNotReservable):
            SolicitationRepository.create(
                requester=admin_user, input=input, session=session
            )


class TestGetById:
    def test_returns_the_matching_solicitation(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        input = _meeting_solicitation_input(
            building=building, schedule_classroom=classroom, requested_classroom=None
        )
        created = SolicitationRepository.create(
            requester=admin_user, input=input, session=session
        )
        session.commit()

        found = SolicitationRepository.get_by_id(
            id=must_be_int(created.id), session=session
        )

        assert found.id == created.id

    def test_raises_when_solicitation_does_not_exist(self, session: Session) -> None:
        with pytest.raises(SolicitationNotFound):
            SolicitationRepository.get_by_id(id=999999, session=session)


class TestGetByUser:
    def test_returns_only_the_users_own_solicitations(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        other_user = UserModelFactory(session=session).create_and_refresh()
        mine = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        SolicitationRepository.create(
            requester=other_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        found = SolicitationRepository.get_by_user(user=admin_user, session=session)

        assert [s.id for s in found] == [mine.id]


class TestGetByBuildingsIds:
    def test_returns_solicitations_of_the_given_buildings(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        found = SolicitationRepository.get_by_buildings_ids(
            building_ids=[must_be_int(building.id)], session=session
        )

        assert solicitation.id in [s.id for s in found]

    def test_excludes_solicitations_of_other_buildings(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        found = SolicitationRepository.get_by_buildings_ids(
            building_ids=[999999], session=session
        )

        assert solicitation.id not in [s.id for s in found]


class TestGetByBuildingsIdsPaginated:
    def test_paginates_solicitations_of_the_given_buildings(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        page = SolicitationRepository.get_by_buildings_ids_paginated(
            building_ids=[must_be_int(building.id)],
            pagination=PaginationInput(page=1, page_size=10),
            session=session,
        )

        assert solicitation.id in [s.id for s in page.items]
        assert page.total_items >= 1


class TestGetByBuildingsIdsOnRange:
    def test_returns_solicitations_created_within_the_range(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        today = date.today()
        found = SolicitationRepository.get_by_buildings_ids_on_range(
            start=today - timedelta(days=1),
            end=today + timedelta(days=1),
            building_ids=[must_be_int(building.id)],
            session=session,
        )

        assert solicitation.id in [s.id for s in found]

    def test_excludes_solicitations_created_outside_the_range(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        found = SolicitationRepository.get_by_buildings_ids_on_range(
            start=date(1999, 1, 1),
            end=date(1999, 12, 31),
            building_ids=[must_be_int(building.id)],
            session=session,
        )

        assert solicitation.id not in [s.id for s in found]


class TestGetPendingByBuildingsIds:
    def test_returns_only_pending_solicitations(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        pending = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        approved = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()
        SolicitationRepository.approve(
            id=must_be_int(approved.id),
            classroom_id=must_be_int(classroom.id),
            user=admin_user,
            session=session,
        )
        session.commit()

        found = SolicitationRepository.get_pending_by_buildings_ids(
            building_ids=[must_be_int(building.id)], session=session
        )

        ids = [s.id for s in found]
        assert pending.id in ids
        assert approved.id not in ids


class TestUpdate:
    def test_updates_capacity_and_delegates_to_the_meeting_repository(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=None,
                capacity=5,
            ),
            session=session,
        )
        session.commit()

        update_input = _meeting_solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
            capacity=20,
        )

        updated = SolicitationRepository.update(
            id=must_be_int(solicitation.id),
            input=update_input,
            user=admin_user,
            session=session,
        )
        session.commit()
        session.refresh(updated)

        assert updated.capacity == 20
        assert updated.solicited_classroom_id == classroom.id

    def test_raises_when_a_different_user_tries_to_update(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        other_user = UserModelFactory(session=session).create_and_refresh()
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        update_input = _meeting_solicitation_input(
            building=building, schedule_classroom=classroom, requested_classroom=None
        )

        with pytest.raises(SolicitationPermissionDenied):
            SolicitationRepository.update(
                id=must_be_int(solicitation.id),
                input=update_input,
                user=other_user,
                session=session,
            )

    def test_raises_when_the_solicitation_is_no_longer_pending(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()
        SolicitationRepository.deny(
            id=must_be_int(solicitation.id),
            input=SolicitationDeny(justification="Sala indisponível"),
            user=admin_user,
            session=session,
        )
        session.commit()

        update_input = _meeting_solicitation_input(
            building=building, schedule_classroom=classroom, requested_classroom=None
        )

        with pytest.raises(SolicitationAlreadyClosed):
            SolicitationRepository.update(
                id=must_be_int(solicitation.id),
                input=update_input,
                user=admin_user,
                session=session,
            )

    def test_raises_when_changing_the_reservation_type(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        update_input = _event_solicitation_input(
            building=building, schedule_classroom=classroom, requested_classroom=None
        )

        with pytest.raises(HTTPException):
            SolicitationRepository.update(
                id=must_be_int(solicitation.id),
                input=update_input,
                user=admin_user,
                session=session,
            )

    def test_raises_when_the_new_classroom_is_not_reservable(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()
        _make_unreservable(classroom, session)

        update_input = _meeting_solicitation_input(
            building=building,
            schedule_classroom=classroom,
            requested_classroom=classroom,
        )

        with pytest.raises(ClassroomNotReservable):
            SolicitationRepository.update(
                id=must_be_int(solicitation.id),
                input=update_input,
                user=admin_user,
                session=session,
            )


class TestApprove:
    def test_approves_using_the_solicited_classroom(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=classroom,
            ),
            session=session,
        )
        session.commit()

        approved = SolicitationRepository.approve(
            id=must_be_int(solicitation.id),
            classroom_id=must_be_int(classroom.id),
            user=admin_user,
            session=session,
        )
        session.commit()
        session.refresh(approved)

        assert approved.get_status() == ReservationStatus.APPROVED
        assert approved.closed_by == admin_user.name
        assert approved.reservation.schedule.allocated is True
        assert approved.reservation.schedule.classroom_id == classroom.id

    def test_raises_when_already_closed(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()
        SolicitationRepository.deny(
            id=must_be_int(solicitation.id),
            input=SolicitationDeny(justification="Sala indisponível"),
            user=admin_user,
            session=session,
        )
        session.commit()

        with pytest.raises(SolicitationAlreadyClosed):
            SolicitationRepository.approve(
                id=must_be_int(solicitation.id),
                classroom_id=must_be_int(classroom.id),
                user=admin_user,
                session=session,
            )

    def test_raises_when_a_required_classroom_does_not_match_the_approved_one(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        other_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=classroom,
                required_classroom=True,
            ),
            session=session,
        )
        session.commit()

        with pytest.raises(SolicitationInvalidClassroom):
            SolicitationRepository.approve(
                id=must_be_int(solicitation.id),
                classroom_id=must_be_int(other_classroom.id),
                user=admin_user,
                session=session,
            )

    def test_can_approve_with_a_different_classroom_when_not_required(
        self,
        admin_user: User,
        building: Building,
        classroom: Classroom,
        session: Session,
    ) -> None:
        other_classroom = ClassroomModelFactory(
            creator=admin_user, building=building, session=session
        ).create_and_refresh()
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building,
                schedule_classroom=classroom,
                requested_classroom=classroom,
                required_classroom=False,
            ),
            session=session,
        )
        session.commit()

        approved = SolicitationRepository.approve(
            id=must_be_int(solicitation.id),
            classroom_id=must_be_int(other_classroom.id),
            user=admin_user,
            session=session,
        )
        session.commit()
        session.refresh(approved)

        assert approved.reservation.schedule.classroom_id == other_classroom.id

    def test_raises_when_the_approved_classroom_belongs_to_a_different_building(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        other_building = BuildingModelFactory(admin_user, session).create_and_refresh()
        other_classroom = ClassroomModelFactory(
            creator=admin_user, building=other_building, session=session
        ).create_and_refresh()
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        with pytest.raises(SolicitationInvalidClassroom):
            SolicitationRepository.approve(
                id=must_be_int(solicitation.id),
                classroom_id=must_be_int(other_classroom.id),
                user=admin_user,
                session=session,
            )


class TestDeny:
    def test_denies_a_pending_solicitation(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        denied = SolicitationRepository.deny(
            id=must_be_int(solicitation.id),
            input=SolicitationDeny(justification="Sala já reservada para outro evento"),
            user=admin_user,
            session=session,
        )
        session.commit()
        session.refresh(denied)

        assert denied.get_status() == ReservationStatus.DENIED
        assert denied.closed_by == admin_user.name
        assert denied.denial_justification == "Sala já reservada para outro evento"

    def test_raises_when_already_closed(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        solicitation = SolicitationRepository.create(
            requester=admin_user,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()
        SolicitationRepository.deny(
            id=must_be_int(solicitation.id),
            input=SolicitationDeny(justification="Sala indisponível"),
            user=admin_user,
            session=session,
        )
        session.commit()

        with pytest.raises(SolicitationAlreadyClosed):
            SolicitationRepository.deny(
                id=must_be_int(solicitation.id),
                input=SolicitationDeny(justification="Segunda tentativa"),
                user=admin_user,
                session=session,
            )


class TestCancel:
    def test_owner_can_cancel_their_own_solicitation(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        requester = UserModelFactory(session=session).create_and_refresh()
        solicitation = SolicitationRepository.create(
            requester=requester,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        cancelled = SolicitationRepository.cancel(
            id=must_be_int(solicitation.id), user=requester, session=session
        )
        session.commit()
        session.refresh(cancelled)

        assert cancelled.get_status() == ReservationStatus.CANCELLED

    def test_admin_can_cancel_someone_elses_solicitation(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        requester = UserModelFactory(session=session).create_and_refresh()
        solicitation = SolicitationRepository.create(
            requester=requester,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        cancelled = SolicitationRepository.cancel(
            id=must_be_int(solicitation.id), user=admin_user, session=session
        )
        session.commit()
        session.refresh(cancelled)

        assert cancelled.get_status() == ReservationStatus.CANCELLED

    def test_raises_when_a_non_admin_tries_to_cancel_someone_elses_solicitation(
        self, admin_user: User, building: Building, classroom: Classroom, session: Session
    ) -> None:
        requester = UserModelFactory(session=session).create_and_refresh()
        other_user = UserModelFactory(session=session).create_and_refresh(
            is_admin=False
        )
        solicitation = SolicitationRepository.create(
            requester=requester,
            input=_meeting_solicitation_input(
                building=building, schedule_classroom=classroom, requested_classroom=None
            ),
            session=session,
        )
        session.commit()

        with pytest.raises(SolicitationPermissionDenied):
            SolicitationRepository.cancel(
                id=must_be_int(solicitation.id), user=other_user, session=session
            )
