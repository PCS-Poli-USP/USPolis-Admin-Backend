"""What a role-only user sees: GET /users/my-access and the "my" listings.

A grant on building A must list A's objects and never B's; a classroom grant
must list that classroom (and its building), not its neighbours.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.subject_db_model import Subject
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from tests.api.roles.conftest import Grants
from tests.factories.model.user_model_factory import UserModelFactory


def _ids(client: TestClient, url: str) -> set[int]:
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.text
    return {item["id"] for item in response.json()}


class TestMyAccess:
    def test_no_role_grants_nothing(self, role_client: TestClient) -> None:
        response = role_client.get("/users/my-access")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["is_admin"] is False
        for scope in body["scopes"].values():
            for grant in scope.values():
                assert grant == {"all": False, "ids": []}

    def test_building_grant_cascades_to_its_classrooms(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
        classroom_b: Classroom,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])

        read = role_client.get("/users/my-access").json()["scopes"]["read"]

        assert read["buildings"] == {"all": False, "ids": [building_a.id]}
        assert read["classrooms"] == {"all": False, "ids": [classroom_a.id]}
        assert read["visible_buildings"] == {"all": False, "ids": [building_a.id]}
        assert role_client.get("/users/my-access").json()["scopes"]["update"][
            "buildings"
        ] == {"all": False, "ids": []}

    def test_classroom_grant_makes_its_building_visible(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
        classroom_a2: Classroom,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.ALLOCATE])

        allocate = role_client.get("/users/my-access").json()["scopes"]["allocate"]

        assert allocate["buildings"] == {"all": False, "ids": []}
        assert allocate["classrooms"] == {"all": False, "ids": [classroom_a.id]}
        assert allocate["visible_buildings"] == {"all": False, "ids": [building_a.id]}

    def test_read_wildcard_grants_everything(
        self, role_client: TestClient, grant: Grants
    ) -> None:
        grant.building(None, [BuildingAction.READ])

        read = role_client.get("/users/my-access").json()["scopes"]["read"]

        assert read["buildings"]["all"] is True
        assert read["classrooms"]["all"] is True

    def test_admin_only_wildcard_is_ignored(
        self, role_client: TestClient, grant: Grants
    ) -> None:
        # Wildcards for UPDATE/DELETE/ALLOCATE/RESERVE/REQUEST are admin-only.
        grant.building(None, [BuildingAction.UPDATE])

        update = role_client.get("/users/my-access").json()["scopes"]["update"]

        assert update["buildings"] == {"all": False, "ids": []}

    def test_admin_gets_everything(self, client: TestClient) -> None:
        body = client.get("/users/my-access").json()

        assert body["is_admin"] is True
        assert all(
            grant["all"]
            for scope in body["scopes"].values()
            for grant in scope.values()
        )


class TestListingsFollowReadGrants:
    def test_without_roles_every_list_is_empty(
        self,
        role_client: TestClient,
        classroom_a: Classroom,
        class_a: Class,
    ) -> None:
        for url in [
            "/users/my-buildings",
            "/users/my-classrooms",
            "/users/my-subjects",
            "/users/my-classes",
            "/users/my-reservations",
        ]:
            assert _ids(role_client, url) == set(), url

    def test_building_grant_lists_that_building_only(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        building_b: Building,
        classroom_a: Classroom,
        classroom_b: Classroom,
        subject_a: Subject,
        subject_b: Subject,
        class_a: Class,
        class_b: Class,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])

        assert _ids(role_client, "/users/my-buildings") == {building_a.id}
        assert _ids(role_client, "/users/my-classrooms") == {classroom_a.id}
        assert _ids(role_client, "/users/my-subjects") == {subject_a.id}
        assert _ids(role_client, "/users/my-classes") == {class_a.id}

    def test_classroom_grant_lists_that_classroom_and_its_building(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
        classroom_a2: Classroom,
        classroom_b: Classroom,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ])

        assert _ids(role_client, "/users/my-classrooms") == {classroom_a.id}
        assert _ids(role_client, "/users/my-buildings") == {building_a.id}

    def test_read_wildcard_lists_everything(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        building_b: Building,
        classroom_a: Classroom,
        classroom_b: Classroom,
    ) -> None:
        grant.classroom(None, [ClassroomAction.READ])

        classrooms = _ids(role_client, "/users/my-classrooms")
        assert {classroom_a.id, classroom_b.id} <= classrooms
        assert {building_a.id, building_b.id} <= _ids(
            role_client, "/users/my-buildings"
        )

    @pytest.mark.parametrize(
        "action",
        [
            ClassroomAction.UPDATE,
            ClassroomAction.DELETE,
            ClassroomAction.ALLOCATE,
            ClassroomAction.RESERVE,
            ClassroomAction.REQUEST,
        ],
    )
    def test_any_action_implies_read(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
        classroom_a2: Classroom,
        action: ClassroomAction,
    ) -> None:
        # A role cannot hold an action on a classroom it cannot read.
        grant.classroom(classroom_a, [action])

        assert _ids(role_client, "/users/my-classrooms") == {classroom_a.id}
        assert role_client.get(f"/classrooms/{classroom_a.id}").status_code == 200

    def test_an_ignored_wildcard_implies_nothing(
        self, role_client: TestClient, grant: Grants, classroom_a: Classroom
    ) -> None:
        # Wildcards for admin-only actions are ignored for non-admins, and so
        # are the READ-on-everything they would otherwise imply.
        grant.classroom(None, [ClassroomAction.RESERVE])

        assert _ids(role_client, "/users/my-classrooms") == set()


class TestUsersOfABuilding:
    """GET /users/{building_id}: to whoever belongs to the building (reads it
    or a classroom in it), with only id, name and email."""

    def test_a_classroom_reader_sees_the_building_users(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
        session: Session,
    ) -> None:
        member = UserModelFactory(session=session).create_and_refresh(
            is_admin=False, buildings=[building_a]
        )
        grant.classroom(classroom_a, [ClassroomAction.READ])

        response = role_client.get(f"/users/{building_a.id}")

        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json() == [
            {"id": member.id, "name": member.name, "email": member.email}
        ]

    def test_refused_on_another_building(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        building_b: Building,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])

        response = role_client.get(f"/users/{building_b.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.text

    def test_refused_with_no_grant(
        self, role_client: TestClient, building_a: Building
    ) -> None:
        response = role_client.get(f"/users/{building_a.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.text
