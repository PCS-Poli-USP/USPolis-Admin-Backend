"""Allocation, bookings, solicitations and conflicts for a role-only user."""

from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.meeting_db_model import Meeting
from server.models.database.solicitation_db_model import Solicitation
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.repositories.occurrence_repository import OccurrenceRepository
from server.repositories.solicitation_repository import SolicitationRepository
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from tests.api.roles.conftest import Grants
from tests.factories.model.meeting_model_factory import MeetingModelFactory
from tests.factories.request.meeting_request_factory import MeetingRequestFactory
from tests.factories.request.solicitation_request_factory import (
    SolicitationRequestFactory,
)

FORBIDDEN = status.HTTP_403_FORBIDDEN


@pytest.fixture(autouse=True)
def no_emails() -> Generator[None, None, None]:
    """Approving, denying and deleting send emails in the background, through
    both EmailService senders. (The suite also blocks SMTP for every test, see
    tests/conftest.py.)"""
    with (
        patch("server.services.email.email_service.EmailService.send_email"),
        patch("server.services.email.email_service.EmailService.send_bcc_email"),
    ):
        yield


def _allocate(client: TestClient, class_: Class, classroom: Classroom) -> int:
    response = client.post(
        "/occurrences/allocate-schedule",
        params={"schedule_id": class_.schedules[0].id, "classroom_id": classroom.id},
    )
    return int(response.status_code)


def _allocate_as_admin(
    admin_user: User, class_: Class, classroom: Classroom, session: Session
) -> None:
    OccurrenceRepository.allocate_schedule(
        user=admin_user,
        classroom=classroom,
        schedule=class_.schedules[0],
        session=session,
    )
    session.commit()
    session.refresh(class_)


class TestAllocation:
    """Moving a schedule takes ALLOCATE on the classroom it leaves and on the
    one it goes to; nothing on the class or its building."""

    def test_allocate_with_allocate_on_the_target_classroom(
        self,
        role_client: TestClient,
        grant: Grants,
        classroom_a: Classroom,
        class_a: Class,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.ALLOCATE])

        assert _allocate(role_client, class_a, classroom_a) == status.HTTP_200_OK

    def test_allocate_is_refused_without_allocate(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
        class_a: Class,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ, BuildingAction.UPDATE])

        assert _allocate(role_client, class_a, classroom_a) == FORBIDDEN

    def test_allocate_is_refused_in_a_classroom_without_the_grant(
        self,
        role_client: TestClient,
        grant: Grants,
        classroom_a: Classroom,
        classroom_a2: Classroom,
        class_a: Class,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.ALLOCATE])

        assert _allocate(role_client, class_a, classroom_a2) == FORBIDDEN

    def test_reallocating_takes_allocate_on_both_classrooms(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        classroom_a: Classroom,
        classroom_a2: Classroom,
        class_a: Class,
        session: Session,
    ) -> None:
        _allocate_as_admin(admin_user, class_a, classroom_a2, session)

        grant.classroom(classroom_a, [ClassroomAction.ALLOCATE])
        assert _allocate(role_client, class_a, classroom_a) == FORBIDDEN

        grant.classroom(classroom_a2, [ClassroomAction.ALLOCATE])
        assert _allocate(role_client, class_a, classroom_a) == status.HTTP_200_OK

    def test_deallocating_takes_allocate_on_the_current_classroom(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        building_a: Building,
        classroom_a: Classroom,
        class_a: Class,
        session: Session,
    ) -> None:
        _allocate_as_admin(admin_user, class_a, classroom_a, session)
        params = {"schedule_id": class_a.schedules[0].id}

        grant.building(building_a, [BuildingAction.READ, BuildingAction.UPDATE])
        refused = role_client.delete(
            "/occurrences/remove-schedule-allocation", params=params
        )
        assert refused.status_code == FORBIDDEN

        grant.classroom(classroom_a, [ClassroomAction.ALLOCATE])
        response = role_client.delete(
            "/occurrences/remove-schedule-allocation", params=params
        )
        assert response.status_code == status.HTTP_200_OK, response.text

    def test_single_occurrence_moves_follow_the_same_rule(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        building_a: Building,
        classroom_a: Classroom,
        classroom_a2: Classroom,
        class_a: Class,
        session: Session,
    ) -> None:
        _allocate_as_admin(admin_user, class_a, classroom_a, session)
        schedule = class_a.schedules[0]
        occurrence = schedule.occurrences[0]
        body = {
            "desalocate": False,
            "all_occurrences": False,
            "start_time": str(occurrence.start_time),
            "end_time": str(occurrence.end_time),
            "building": building_a.name,
            "classroom": classroom_a2.name,
            "occurrence_id": occurrence.id,
            "schedule_id": schedule.id,
        }

        grant.classroom(classroom_a2, [ClassroomAction.ALLOCATE])
        assert role_client.patch("/allocations/events", json=body).status_code == (
            FORBIDDEN
        )
        deallocate = {**body, "desalocate": True}
        assert (
            role_client.patch("/allocations/events", json=deallocate).status_code
            == FORBIDDEN
        )

        grant.classroom(classroom_a, [ClassroomAction.ALLOCATE])
        moved = role_client.patch("/allocations/events", json=body)
        assert moved.status_code == status.HTTP_200_OK, moved.text

    def test_allocation_map_takes_allocate_on_the_target_classrooms(
        self,
        role_client: TestClient,
        grant: Grants,
        classroom_a: Classroom,
        classroom_a2: Classroom,
        class_a: Class,
    ) -> None:
        body = {
            "allocation_map": [
                {
                    "schedule_id": class_a.schedules[0].id,
                    "classroom_ids": [classroom_a.id, classroom_a2.id],
                }
            ]
        }
        grant.classroom(classroom_a, [ClassroomAction.ALLOCATE])
        grant.classroom(classroom_a2, [ClassroomAction.READ])
        refused = role_client.post("/allocations/allocate-allocation-map", json=body)
        assert refused.status_code == FORBIDDEN

        grant.classroom(classroom_a2, [ClassroomAction.ALLOCATE])
        response = role_client.post("/allocations/allocate-allocation-map", json=body)
        assert response.status_code == status.HTTP_200_OK, response.text

    def test_a_class_goes_only_into_its_subject_buildings(
        self,
        role_client: TestClient,
        grant: Grants,
        classroom_b: Classroom,
        class_a: Class,
    ) -> None:
        # class_a's subject is only in building A: a classroom of B is refused
        # even with ALLOCATE on it (400: a consistency rule, not a permission).
        grant.classroom(classroom_b, [ClassroomAction.ALLOCATE])

        response = role_client.post(
            "/occurrences/allocate-schedule",
            params={
                "schedule_id": class_a.schedules[0].id,
                "classroom_id": classroom_b.id,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "não está no prédio" in response.json()["detail"]

    def test_a_subject_in_both_buildings_allocates_in_either(
        self,
        role_client: TestClient,
        grant: Grants,
        building_b: Building,
        classroom_b: Classroom,
        subject_a: Subject,
        class_a: Class,
        session: Session,
    ) -> None:
        subject_a.buildings.append(building_b)
        session.add(subject_a)
        session.commit()
        grant.classroom(classroom_b, [ClassroomAction.ALLOCATE])

        assert _allocate(role_client, class_a, classroom_b) == status.HTTP_200_OK

    def test_a_single_occurrence_cannot_leave_its_subject_buildings(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        building_b: Building,
        classroom_a: Classroom,
        classroom_b: Classroom,
        class_a: Class,
        session: Session,
    ) -> None:
        _allocate_as_admin(admin_user, class_a, classroom_a, session)
        schedule = class_a.schedules[0]
        occurrence = schedule.occurrences[0]
        grant.classroom(classroom_a, [ClassroomAction.ALLOCATE])
        grant.classroom(classroom_b, [ClassroomAction.ALLOCATE])

        response = role_client.patch(
            "/allocations/events",
            json={
                "desalocate": False,
                "all_occurrences": False,
                "start_time": str(occurrence.start_time),
                "end_time": str(occurrence.end_time),
                "building": building_b.name,
                "classroom": classroom_b.name,
                "occurrence_id": occurrence.id,
                "schedule_id": schedule.id,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admins_are_bound_to_the_subject_buildings_too(
        self, client: TestClient, classroom_b: Classroom, class_a: Class
    ) -> None:
        # Otherwise the class would be invisible to building B's users.
        assert _allocate(client, class_a, classroom_b) == status.HTTP_400_BAD_REQUEST

    def test_classroom_level_role_reads_classes_in_its_classroom(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        classroom_a: Classroom,
        class_a: Class,
        session: Session,
    ) -> None:
        # What a migrated non-main group looks like: grants on its classrooms
        # only, nothing on the building.
        _allocate_as_admin(admin_user, class_a, classroom_a, session)
        grant.classroom(classroom_a, [ClassroomAction.READ])

        assert role_client.get(f"/classes/{class_a.id}").status_code == 200

    def test_classroom_level_role_only_reads_classes_elsewhere(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        classroom_a: Classroom,
        classroom_a2: Classroom,
        class_a: Class,
        session: Session,
    ) -> None:
        # Belonging to building A (a classroom of A) reads every class of A's
        # subjects, but changes only follow the classroom of the schedule.
        _allocate_as_admin(admin_user, class_a, classroom_a2, session)
        grant.classroom(classroom_a, [ClassroomAction.UPDATE, ClassroomAction.ALLOCATE])

        assert role_client.get(f"/classes/{class_a.id}").status_code == 200
        response = role_client.delete(
            "/occurrences/remove-schedule-allocation",
            params={"schedule_id": class_a.schedules[0].id},
        )
        assert response.status_code == FORBIDDEN

    def test_allocation_logs_with_read(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        building_b: Building,
        class_a: Class,
        class_b: Class,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])

        ok = role_client.get(f"/allocations_logs/{class_a.schedules[0].id}")
        other = role_client.get(f"/allocations_logs/{class_b.schedules[0].id}")

        assert ok.status_code == status.HTTP_200_OK, ok.text
        assert other.status_code == status.HTTP_404_NOT_FOUND


def _meeting_in(admin_user: User, classroom: Classroom, session: Session) -> Meeting:
    """A meeting whose schedule is allocated in `classroom` (the factory leaves
    the schedule without one)."""
    meeting = MeetingModelFactory(
        classroom=classroom, creator=admin_user, session=session
    ).create_and_refresh()
    OccurrenceRepository.allocate_schedule(
        user=admin_user,
        classroom=classroom,
        schedule=meeting.reservation.schedule,
        session=session,
    )
    session.commit()
    session.refresh(meeting)
    return meeting


class TestBookings:
    def test_create_meeting_with_classroom_reserve(
        self, role_client: TestClient, grant: Grants, classroom_a: Classroom
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.RESERVE])
        body = jsonable_encoder(MeetingRequestFactory(classroom_a).create_input())

        response = role_client.post("/reservations/meetings", json=body)

        assert response.status_code == status.HTTP_201_CREATED, response.text

    def test_create_meeting_through_a_building_reserve(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
    ) -> None:
        grant.building(building_a, [BuildingAction.RESERVE])
        body = jsonable_encoder(MeetingRequestFactory(classroom_a).create_input())

        response = role_client.post("/reservations/meetings", json=body)

        assert response.status_code == status.HTTP_201_CREATED, response.text

    def test_create_meeting_is_refused_without_reserve(
        self,
        role_client: TestClient,
        grant: Grants,
        classroom_a: Classroom,
        classroom_a2: Classroom,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ, ClassroomAction.UPDATE])
        grant.classroom(classroom_a2, [ClassroomAction.RESERVE])
        body = jsonable_encoder(MeetingRequestFactory(classroom_a).create_input())

        response = role_client.post("/reservations/meetings", json=body)

        assert response.status_code == FORBIDDEN

    def test_update_and_delete_meeting_with_reserve(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        classroom_a: Classroom,
        session: Session,
    ) -> None:
        meeting = _meeting_in(admin_user, classroom_a, session)
        grant.classroom(classroom_a, [ClassroomAction.RESERVE])
        body = jsonable_encoder(MeetingRequestFactory(classroom_a).update_input())

        updated = role_client.put(f"/reservations/meetings/{meeting.id}", json=body)
        deleted = role_client.delete(f"/reservations/{meeting.reservation_id}")

        assert updated.status_code == status.HTTP_200_OK, updated.text
        assert deleted.status_code == status.HTTP_200_OK, deleted.text

    def test_my_reservations_lists_readable_classrooms(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        classroom_a: Classroom,
        classroom_b: Classroom,
        session: Session,
    ) -> None:
        mine = _meeting_in(admin_user, classroom_a, session)
        _meeting_in(admin_user, classroom_b, session)
        grant.classroom(classroom_a, [ClassroomAction.READ])

        response = role_client.get("/users/my-reservations")

        assert {r["id"] for r in response.json()} == {mine.reservation_id}


def _solicitation(
    admin_user: User, building: Building, classroom: Classroom, session: Session
) -> Solicitation:
    solicitation = SolicitationRepository.create(
        requester=admin_user,
        input=SolicitationRequestFactory(building, classroom).create_input(
            required_classroom=False
        ),
        session=session,
    )
    session.commit()
    session.refresh(solicitation)
    return solicitation


class TestSolicitations:
    def test_pending_inbox_follows_reserve(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        building_a: Building,
        building_b: Building,
        classroom_a: Classroom,
        classroom_b: Classroom,
        session: Session,
    ) -> None:
        mine = _solicitation(admin_user, building_a, classroom_a, session)
        _solicitation(admin_user, building_b, classroom_b, session)

        grant.classroom(classroom_a, [ClassroomAction.READ])
        assert role_client.get("/solicitations/pending").json() == []

        grant.classroom(classroom_a, [ClassroomAction.RESERVE])
        pending = role_client.get("/solicitations/pending").json()
        assert {s["id"] for s in pending} == {mine.id}

    def test_approve_with_reserve(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        building_a: Building,
        classroom_a: Classroom,
        session: Session,
    ) -> None:
        solicitation = _solicitation(admin_user, building_a, classroom_a, session)
        grant.classroom(classroom_a, [ClassroomAction.RESERVE])

        response = role_client.put(
            f"/solicitations/approve/{solicitation.id}",
            json={"classroom_id": classroom_a.id, "classroom_name": classroom_a.name},
        )

        assert response.status_code == status.HTTP_200_OK, response.text

    def test_approve_and_deny_are_refused_without_reserve(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        building_a: Building,
        classroom_a: Classroom,
        session: Session,
    ) -> None:
        solicitation = _solicitation(admin_user, building_a, classroom_a, session)
        grant.classroom(classroom_a, [ClassroomAction.READ, ClassroomAction.UPDATE])

        approve = role_client.put(
            f"/solicitations/approve/{solicitation.id}",
            json={"classroom_id": classroom_a.id, "classroom_name": classroom_a.name},
        )
        deny = role_client.put(
            f"/solicitations/deny/{solicitation.id}", json={"justification": "Não"}
        )

        assert approve.status_code == FORBIDDEN
        assert deny.status_code == FORBIDDEN

    def test_deny_with_reserve(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        building_a: Building,
        classroom_a: Classroom,
        session: Session,
    ) -> None:
        solicitation = _solicitation(admin_user, building_a, classroom_a, session)
        grant.classroom(classroom_a, [ClassroomAction.RESERVE])

        response = role_client.put(
            f"/solicitations/deny/{solicitation.id}", json={"justification": "Não"}
        )

        assert response.status_code == status.HTTP_200_OK, response.text


class TestConflicts:
    def test_building_conflicts_cover_readable_classrooms(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
        classroom_a2: Classroom,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ])

        response = role_client.get(
            f"/conflicts/building/{building_a.id}", params={"type": "unintentional"}
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        assert {c["id"] for c in response.json()["conflicts"]} <= {classroom_a.id}

    def test_building_conflicts_are_refused_without_read(
        self, role_client: TestClient, building_a: Building
    ) -> None:
        response = role_client.get(
            f"/conflicts/building/{building_a.id}", params={"type": "unintentional"}
        )

        assert response.status_code == FORBIDDEN


class TestClassroomsWithConflictCount:
    """Both conflict-count routes (the allocation modal): whoever belongs to
    the building gets the classrooms of it they can read."""

    _BODY = {
        "start_time": "08:00:00",
        "end_time": "10:00:00",
        "recurrence": "Custom",
        "dates": ["2026-03-02"],
    }

    @staticmethod
    def _post(client: TestClient, building: Building) -> tuple[int, set[int]]:
        response = client.post(
            f"/classrooms/with-conflict-count/{building.id}",
            json=TestClassroomsWithConflictCount._BODY,
        )
        ids = (
            {c["id"] for c in response.json()} if response.status_code == 200 else set()
        )
        return response.status_code, ids

    def test_post_lists_the_readable_classrooms(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
        classroom_a2: Classroom,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ])

        assert self._post(role_client, building_a) == (200, {classroom_a.id})

    def test_post_with_building_read_lists_all_of_it(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
        classroom_a2: Classroom,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])

        assert self._post(role_client, building_a) == (
            200,
            {classroom_a.id, classroom_a2.id},
        )

    def test_post_is_refused_on_another_building(
        self,
        role_client: TestClient,
        grant: Grants,
        building_b: Building,
        classroom_a: Classroom,
        classroom_b: Classroom,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ])

        assert self._post(role_client, building_b) == (FORBIDDEN, set())

    def test_get_for_a_schedule_lists_the_readable_classrooms(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
        classroom_a2: Classroom,
        class_a: Class,
    ) -> None:
        # A classroom-level role allocates: the modal must list its classroom
        # (before, the route required READ on the whole building).
        grant.classroom(classroom_a, [ClassroomAction.ALLOCATE])

        response = role_client.get(
            f"/classrooms/with-conflict-count/{building_a.id}/{class_a.schedules[0].id}"
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        assert {c["id"] for c in response.json()} == {classroom_a.id}

    def test_get_is_refused_on_another_building(
        self,
        role_client: TestClient,
        grant: Grants,
        building_b: Building,
        classroom_a: Classroom,
        classroom_b: Classroom,
        class_a: Class,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ])

        response = role_client.get(
            f"/classrooms/with-conflict-count/{building_b.id}/{class_a.schedules[0].id}"
        )

        assert response.status_code == FORBIDDEN


class TestAllocationReuseOptions:
    """POST /allocations/reuse-options: READ on every class asked for."""

    @staticmethod
    def _options(client: TestClient, building: Building, *classes: Class) -> int:
        response = client.post(
            "/allocations/reuse-options",
            json={
                "building_id": building.id,
                "allocation_year": 2025,
                "targets": [
                    {"subject_id": class_.subject_id, "class_ids": [class_.id]}
                    for class_ in classes
                ],
            },
        )
        return int(response.status_code)

    def test_with_read_on_the_class(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        class_a: Class,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])

        assert self._options(role_client, building_a, class_a) == 200

    def test_refused_for_a_class_of_another_building(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        class_a: Class,
        class_b: Class,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])

        assert self._options(role_client, building_a, class_a, class_b) == FORBIDDEN
