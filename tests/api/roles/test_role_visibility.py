"""Read-only visibility of classes and subjects (the "Cálculo 1" convention).

A subject can be added to several buildings. Whoever belongs to one of them
(can read the building, or any classroom in it) sees every class of that
subject, read-only, allocated or not, even classes whose schedules are in
another building's classrooms: a class can have one schedule in each building,
and both sides need to see it. Writing still follows the classroom (or, for an
unallocated schedule, the building).
"""

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.repositories.occurrence_repository import OccurrenceRepository
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from tests.api.roles.conftest import Grants
from tests.factories.request.class_request_factory import ClassRequestFactory

FORBIDDEN = status.HTTP_403_FORBIDDEN


def _shared_subject_class_in_b(
    *,
    admin_user: User,
    subject_a: Subject,
    building_b: Building,
    class_a: Class,
    classroom_b: Classroom,
    session: Session,
) -> Class:
    """class_a's subject is in buildings A and B; its schedule is allocated in
    a classroom of B."""
    subject_a.buildings.append(building_b)
    session.add(subject_a)
    session.commit()
    OccurrenceRepository.allocate_schedule(
        user=admin_user,
        classroom=classroom_b,
        schedule=class_a.schedules[0],
        session=session,
    )
    session.commit()
    session.refresh(class_a)
    return class_a


class TestSubjectInMyBuilding:
    def test_building_user_reads_a_class_allocated_in_another_building(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        building_a: Building,
        building_b: Building,
        classroom_b: Classroom,
        subject_a: Subject,
        class_a: Class,
        session: Session,
    ) -> None:
        class_ = _shared_subject_class_in_b(
            admin_user=admin_user,
            subject_a=subject_a,
            building_b=building_b,
            class_a=class_a,
            classroom_b=classroom_b,
            session=session,
        )
        grant.building(building_a, [BuildingAction.READ, BuildingAction.UPDATE])

        assert role_client.get(f"/classes/{class_.id}").status_code == 200
        listed = {c["id"] for c in role_client.get("/users/my-classes").json()}
        assert class_.id in listed

        # Read-only: the schedule is in B, so A's grants do not edit it.
        body = jsonable_encoder(ClassRequestFactory(subject_a).update_input())
        assert role_client.put(f"/classes/{class_.id}", json=body).status_code == (
            FORBIDDEN
        )

    def test_classroom_level_user_is_a_user_of_the_building(
        self,
        role_client: TestClient,
        grant: Grants,
        admin_user: User,
        building_b: Building,
        classroom_a: Classroom,
        classroom_b: Classroom,
        subject_a: Subject,
        class_a: Class,
        session: Session,
    ) -> None:
        # Reading one classroom of A is enough to belong to A (what a legacy
        # non-main group of A gave).
        class_ = _shared_subject_class_in_b(
            admin_user=admin_user,
            subject_a=subject_a,
            building_b=building_b,
            class_a=class_a,
            classroom_b=classroom_b,
            session=session,
        )
        grant.classroom(classroom_a, [ClassroomAction.READ])

        assert role_client.get(f"/classes/{class_.id}").status_code == 200
        assert role_client.get(f"/subjects/{subject_a.id}").status_code == 200
        listed = {c["id"] for c in role_client.get("/users/my-classes").json()}
        assert class_.id in listed

    def test_subject_outside_my_buildings_is_not_visible(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_b: Subject,
        class_b: Class,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])

        assert role_client.get(f"/classes/{class_b.id}").status_code == FORBIDDEN
        assert role_client.get(f"/subjects/{subject_b.id}").status_code == FORBIDDEN
        listed = {c["id"] for c in role_client.get("/users/my-classes").json()}
        assert class_b.id not in listed

    def test_listing_and_reading_agree(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        class_a: Class,
        class_b: Class,
    ) -> None:
        # Whatever the list shows, GET by id returns, and nothing else.
        grant.building(building_a, [BuildingAction.READ])

        for item in role_client.get("/users/my-classes").json():
            assert role_client.get(f"/classes/{item['id']}").status_code == 200
        for item in role_client.get("/users/my-subjects").json():
            assert role_client.get(f"/subjects/{item['id']}").status_code == 200
