"""Who handles a solicitation (emails, approve/deny): the groups of its
allocated or solicited classroom, or, with no classroom, only the building
main group. A group restricted to one classroom must not get the others."""

from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.group_db_model import Group
from server.models.database.solicitation_db_model import Solicitation
from server.models.database.user_db_model import User
from server.models.http.requests.solicitation_request_models import (
    MeetingSolicitation,
    SolicitationRegister,
)
from server.models.page_models import PaginationInput
from server.repositories.meeting_repository import MeetingRepository
from server.repositories.solicitation_repository import SolicitationRepository
from server.services.security.solicitation_permission_checker import (
    ForbiddenSolicitationAccess,
    SolicitationPermissionChecker,
)
from server.utils.enums.reservation_status import ReservationStatus
from server.utils.enums.reservation_type import ReservationType
from server.utils.must_be_int import must_be_int
from tests.factories.model.classroom_model_factory import ClassroomModelFactory
from tests.factories.model.group_model_factory import GroupModelFactory
from tests.factories.model.reservation_model_factory import ReservationModelFactory
from tests.factories.model.solicitation_model_factory import (
    SolicitationModelFactory,
)
from tests.factories.model.user_model_factory import UserModelFactory
from tests.factories.request.meeting_request_factory import MeetingRequestFactory


@pytest.fixture
def room_a(user: User, building: Building, session: Session) -> Classroom:
    return ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_and_refresh()


@pytest.fixture
def room_b(user: User, building: Building, session: Session) -> Classroom:
    return ClassroomModelFactory(
        creator=user, building=building, session=session
    ).create_and_refresh()


@pytest.fixture
def room_a_group(
    building: Building, room_a: Classroom, restricted_user: User, session: Session
) -> Group:
    """A group with a single classroom, holding the restricted user."""
    group = GroupModelFactory(building, session).create_and_refresh(
        classrooms=[room_a], users=[restricted_user]
    )
    session.refresh(restricted_user)
    return group


@pytest.fixture
def building_admin(building: Building, session: Session) -> User:
    """A member of the building main group (access to every classroom)."""
    admin = UserModelFactory(session=session).create_and_refresh(
        is_admin=False, buildings=[building]
    )
    main_group = building.get_main_group()
    main_group.users.append(admin)
    session.add(main_group)
    session.commit()
    session.refresh(admin)
    return admin


Solicit = Callable[[Classroom | None], Solicitation]


@pytest.fixture
def solicit(
    building: Building, common_user: User, room_a: Classroom, session: Session
) -> Solicit:
    """Make a pending solicitation, optionally for a classroom."""

    def make(solicited: Classroom | None) -> Solicitation:
        reservation = ReservationModelFactory(
            reservation_type=ReservationType.MEETING,
            creator=common_user,
            classroom=room_a,
            session=session,
        ).create_and_refresh(status=ReservationStatus.PENDING)
        return SolicitationModelFactory(
            building=building,
            requester=common_user,
            reservation=reservation,
            session=session,
            solicited_classroom=solicited,
        ).create_and_refresh()

    return make


@pytest.mark.usefixtures("room_a_group")
class TestAdministrativeUsers:
    def test_another_classroom_goes_only_to_its_groups_and_the_main_group(
        self, solicit: Solicit, room_b: Classroom, building_admin: User
    ) -> None:
        solicitation = solicit(room_b)

        assert solicitation.get_administrative_users() == [building_admin]

    def test_the_groups_classroom_goes_to_the_group_and_the_main_group(
        self,
        solicit: Solicit,
        room_a: Classroom,
        restricted_user: User,
        building_admin: User,
    ) -> None:
        solicitation = solicit(room_a)

        assert set(solicitation.get_administrative_users()) == {
            restricted_user,
            building_admin,
        }

    def test_no_classroom_goes_only_to_the_main_group(
        self, solicit: Solicit, building_admin: User
    ) -> None:
        solicitation = solicit(None)

        assert solicitation.get_administrative_users() == [building_admin]

    def test_the_allocated_classroom_wins_over_the_solicited_one(
        self,
        solicit: Solicit,
        room_a: Classroom,
        room_b: Classroom,
        restricted_user: User,
        session: Session,
    ) -> None:
        solicitation = solicit(room_b)
        solicitation.reservation.schedule.classroom = room_a
        session.commit()

        assert restricted_user in solicitation.get_administrative_users()

    def test_users_who_opted_out_get_no_email(
        self,
        solicit: Solicit,
        room_a: Classroom,
        restricted_user: User,
        building_admin: User,
        session: Session,
    ) -> None:
        building_admin.receive_emails = False
        session.commit()
        solicitation = solicit(room_a)

        assert solicitation.get_administrative_users_for_email() == [restricted_user]


def test_listing_a_classrooms_users_does_not_link_it_to_the_main_group(
    room_a: Classroom, room_a_group: Group, building: Building, session: Session
) -> None:
    assert building.main_group in room_a.get_groups()

    session.commit()
    session.refresh(room_a)

    assert room_a.groups == [room_a_group]


@pytest.mark.usefixtures("room_a_group")
class TestPermissionChecker:
    def test_a_single_classroom_group_only_handles_that_classroom(
        self,
        solicit: Solicit,
        room_a: Classroom,
        room_b: Classroom,
        restricted_user: User,
        session: Session,
    ) -> None:
        checker = SolicitationPermissionChecker(restricted_user, session)

        checker.check_permission(solicit(room_a))
        for solicitation in (solicit(room_b), solicit(None)):
            with pytest.raises(ForbiddenSolicitationAccess):
                checker.check_permission(solicitation)

    def test_the_main_group_handles_everything(
        self,
        solicit: Solicit,
        room_a: Classroom,
        room_b: Classroom,
        building_admin: User,
        session: Session,
    ) -> None:
        checker = SolicitationPermissionChecker(building_admin, session)

        for solicitation in (solicit(room_a), solicit(room_b), solicit(None)):
            checker.check_permission(solicitation)


@pytest.mark.usefixtures("room_a_group")
class TestDenyRoute:
    URL = "/solicitations/deny"

    @pytest.fixture(autouse=True)
    def no_email(self) -> Generator[None, None, None]:
        with patch(
            "server.routes.restricted.solicitation_routes.EmailService.send_solicitation_denied_email",
            new_callable=AsyncMock,
        ):
            yield

    def test_cannot_deny_another_classrooms_solicitation(
        self, solicit: Solicit, room_b: Classroom, restricted_client: TestClient
    ) -> None:
        solicitation = solicit(room_b)

        response = restricted_client.put(
            f"{self.URL}/{solicitation.id}", json={"justification": "x"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert solicitation.get_status() == ReservationStatus.PENDING

    def test_can_deny_its_classrooms_solicitation(
        self, solicit: Solicit, room_a: Classroom, restricted_client: TestClient
    ) -> None:
        solicitation = solicit(room_a)

        response = restricted_client.put(
            f"{self.URL}/{solicitation.id}", json={"justification": "x"}
        )

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("room_a_group")
class TestListing:
    """Listings follow the same rule: a group restricted to some classrooms
    only sees those classrooms' solicitations."""

    @pytest.fixture
    def solicitations(
        self, solicit: Solicit, room_a: Classroom, room_b: Classroom
    ) -> dict[str, Solicitation]:
        return {
            "room_a": solicit(room_a),
            "room_b": solicit(room_b),
            "none": solicit(None),
        }

    def ids(self, *solicitations: Solicitation) -> set[int]:
        return {must_be_int(solicitation.id) for solicitation in solicitations}

    def test_a_single_classroom_group_only_sees_that_classroom(
        self,
        solicitations: dict[str, Solicitation],
        restricted_client: TestClient,
    ) -> None:
        paginated = restricted_client.get("/solicitations").json()
        pending = restricted_client.get("/solicitations/pending").json()

        expected = self.ids(solicitations["room_a"])
        assert {item["id"] for item in paginated["data"]} == expected
        assert paginated["total_items"] == 1
        assert {item["id"] for item in pending} == expected

    def test_the_allocated_classroom_wins_over_the_solicited_one(
        self,
        solicitations: dict[str, Solicitation],
        room_a: Classroom,
        restricted_user: User,
        building: Building,
        session: Session,
    ) -> None:
        moved = solicitations["room_b"]
        moved.reservation.schedule.classroom = room_a
        session.commit()

        found = SolicitationRepository.get_pending_by_buildings_ids(
            building_ids=[must_be_int(building.id)],
            user=restricted_user,
            session=session,
        )

        assert self.ids(*found) == self.ids(solicitations["room_a"], moved)

    def test_the_main_group_sees_everything_in_its_building(
        self,
        solicitations: dict[str, Solicitation],
        building_admin: User,
        building: Building,
        session: Session,
    ) -> None:
        page = SolicitationRepository.get_by_buildings_ids_paginated(
            building_ids=[must_be_int(building.id)],
            user=building_admin,
            pagination=PaginationInput(page=1, page_size=10),
            session=session,
        )

        assert self.ids(*page.items) == self.ids(*solicitations.values())

    def test_a_user_without_groups_sees_nothing(
        self,
        solicitations: dict[str, Solicitation],
        common_user: User,
        building: Building,
        session: Session,
    ) -> None:
        found = SolicitationRepository.get_pending_by_buildings_ids(
            building_ids=[must_be_int(building.id)],
            user=common_user,
            session=session,
        )

        assert found == []


class TestEditingNeverBooksTheClassroom:
    """Only approve() books a classroom. Editing a pending solicitation used
    to recreate its schedule with allocate=True, taking the classroom (and
    keeping it even if the solicitation was later denied) with no approval."""

    @pytest.fixture(autouse=True)
    def no_email(self) -> Generator[None, None, None]:
        with patch(
            "server.routes.authenticated.solicitation_routes.EmailService.send_solicitation_request_email",
            new_callable=AsyncMock,
        ):
            yield

    def payload(
        self, building: Building, classroom: Classroom, booked: Classroom | None
    ) -> dict[str, Any]:
        meeting = MeetingRequestFactory(classroom).create_input()
        data = MeetingSolicitation(
            **{**meeting.model_dump(), "classroom_id": booked.id if booked else None}
        )
        register = SolicitationRegister(
            capacity=10,
            required_classroom=False,
            building_id=must_be_int(building.id),
            reservation_data=data,
        )
        body: dict[str, Any] = jsonable_encoder(register)
        return body

    def assert_not_booked(self, solicitation_id: int, session: Session) -> None:
        session.expire_all()
        solicitation = SolicitationRepository.get_by_id(
            id=solicitation_id, session=session
        )
        schedule = solicitation.reservation.schedule
        assert solicitation.get_status() == ReservationStatus.PENDING
        assert not schedule.allocated
        assert schedule.occurrences == [] or all(
            occurrence.classroom_id is None for occurrence in schedule.occurrences
        )

    @pytest.mark.parametrize("first", ["room_b", None])
    def test_editing_to_a_classroom_does_not_book_it(
        self,
        first: str | None,
        request: pytest.FixtureRequest,
        building: Building,
        room_a: Classroom,
        common_client: TestClient,
        session: Session,
    ) -> None:
        first_room = request.getfixturevalue(first) if first else None
        created = common_client.post(
            "/solicitations", json=self.payload(building, room_a, first_room)
        )
        assert created.status_code == status.HTTP_200_OK
        solicitation_id = created.json()["id"]
        self.assert_not_booked(solicitation_id, session)

        edited = common_client.put(
            f"/solicitations/{solicitation_id}",
            json=self.payload(building, room_a, room_a),
        )

        assert edited.status_code == status.HTTP_200_OK
        self.assert_not_booked(solicitation_id, session)

    def test_no_other_edit_path_books_an_unapproved_reservation(
        self,
        user: User,
        building: Building,
        room_a: Classroom,
        common_client: TestClient,
        session: Session,
    ) -> None:
        """E.g. PUT /reservations/meetings/{id}, which allocates by default."""
        created = common_client.post(
            "/solicitations", json=self.payload(building, room_a, None)
        )
        solicitation_id = created.json()["id"]
        meeting = SolicitationRepository.get_by_id(
            id=solicitation_id, session=session
        ).reservation.meeting
        assert meeting is not None

        MeetingRepository.update(
            user=user,
            id=must_be_int(meeting.id),
            input=MeetingRequestFactory(room_a).update_input(),
            session=session,
        )
        session.commit()

        self.assert_not_booked(solicitation_id, session)


@pytest.mark.usefixtures("room_a_group")
class TestCreateRouteRecipients:
    """Through the real route: recipients are computed before the commit,
    when the new schedule only has classroom_id (its classroom relationship
    still reads None). That used to send the email to every group of the
    building even for a solicitation with a classroom."""

    @pytest.fixture
    def send(self) -> Generator[AsyncMock, None, None]:
        with patch(
            "server.routes.authenticated.solicitation_routes.EmailService.send_solicitation_request_email",
            new_callable=AsyncMock,
        ) as send:
            yield send

    def recipients(
        self,
        send: AsyncMock,
        client: TestClient,
        building: Building,
        room_a: Classroom,
        booked: Classroom | None,
    ) -> set[int]:
        response = client.post(
            "/solicitations",
            json=TestEditingNeverBooksTheClassroom().payload(building, room_a, booked),
        )
        assert response.status_code == status.HTTP_200_OK
        users: list[User] = send.call_args.args[0]
        return {must_be_int(user.id) for user in users}

    def test_another_classroom_skips_the_single_classroom_group(
        self,
        send: AsyncMock,
        common_client: TestClient,
        building: Building,
        room_a: Classroom,
        room_b: Classroom,
        restricted_user: User,
        building_admin: User,
    ) -> None:
        got = self.recipients(send, common_client, building, room_a, room_b)

        assert got == {must_be_int(building_admin.id)}

    def test_its_classroom_reaches_the_single_classroom_group(
        self,
        send: AsyncMock,
        common_client: TestClient,
        building: Building,
        room_a: Classroom,
        restricted_user: User,
        building_admin: User,
    ) -> None:
        got = self.recipients(send, common_client, building, room_a, room_a)

        assert got == {must_be_int(restricted_user.id), must_be_int(building_admin.id)}

    def test_no_classroom_reaches_only_the_main_group(
        self,
        send: AsyncMock,
        common_client: TestClient,
        building: Building,
        room_a: Classroom,
        building_admin: User,
    ) -> None:
        got = self.recipients(send, common_client, building, room_a, None)

        assert got == {must_be_int(building_admin.id)}


@pytest.mark.usefixtures("room_a_group")
class TestApproveRouteMessage:
    """The approver can add a note to the approval email; it is not stored."""

    @pytest.fixture
    def send(self) -> Generator[AsyncMock, None, None]:
        with patch(
            "server.routes.restricted.solicitation_routes.EmailService.send_solicitation_approved_email",
            new_callable=AsyncMock,
        ) as send:
            yield send

    @pytest.mark.parametrize(
        ("sent", "expected"),
        [
            ("  Retire a chave na portaria.  ", "Retire a chave na portaria."),
            (None, None),
        ],
    )
    def test_the_message_goes_to_the_email(
        self,
        sent: str | None,
        expected: str | None,
        send: AsyncMock,
        solicit: Solicit,
        room_a: Classroom,
        restricted_client: TestClient,
    ) -> None:
        solicitation = solicit(room_a)
        body: dict[str, Any] = {
            "classroom_id": room_a.id,
            "classroom_name": room_a.name,
        }
        if sent is not None:
            body["message"] = sent

        response = restricted_client.put(
            f"/solicitations/approve/{solicitation.id}", json=body
        )

        assert response.status_code == status.HTTP_200_OK
        assert send.call_args.args[0].message == expected
