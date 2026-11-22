"""Classrooms, subjects and classes for a role-only user.

One test per row of the action table in docs/PERMISSIONS.md: the grant makes
the request succeed, and the same request is refused without it (or with the
grant on the other building).
"""

from unittest.mock import AsyncMock, patch

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.classroom_db_model import Classroom
from server.models.database.subject_db_model import Subject
from server.models.http.responses.subject_response_models import (
    SubjectCrawlResponse,
)
from server.repositories.subject_repository import SubjectRepository
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.enums.crawler_enums import CrawlerType
from server.utils.must_be_int import must_be_int
from tests.api.roles.conftest import Grants
from tests.factories.request.class_request_factory import ClassRequestFactory
from tests.factories.request.classroom_request_factory import (
    ClassroomRequestFactory,
)
from tests.factories.request.subject_request_factory import SubjectRequestFactory

FORBIDDEN = status.HTTP_403_FORBIDDEN


def _classroom_body(building: Building) -> dict:
    """A classroom for `building` with no group: roles do not need one."""
    factory = ClassroomRequestFactory(group=building.get_main_group())
    body: dict = jsonable_encoder(
        factory.create_input(building_id=must_be_int(building.id), group_ids=[])
    )
    return body


class TestClassrooms:
    def test_create_without_a_group_with_building_create(
        self, role_client: TestClient, grant: Grants, building_a: Building
    ) -> None:
        grant.building(building_a, [BuildingAction.CREATE])

        response = role_client.post("/classrooms", json=_classroom_body(building_a))

        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json()["building_id"] == building_a.id

    def test_create_is_refused_without_building_create(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        building_b: Building,
    ) -> None:
        grant.building(building_b, [BuildingAction.CREATE])
        grant.building(building_a, [BuildingAction.READ, BuildingAction.UPDATE])

        response = role_client.post("/classrooms", json=_classroom_body(building_a))

        assert response.status_code == FORBIDDEN

    def test_read_with_classroom_read(
        self, role_client: TestClient, grant: Grants, classroom_a: Classroom
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ])

        response = role_client.get(f"/classrooms/{classroom_a.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == classroom_a.id

    def test_read_through_a_building_grant(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])

        response = role_client.get(f"/classrooms/{classroom_a.id}")

        assert response.status_code == status.HTTP_200_OK

    def test_read_is_refused_for_another_classroom(
        self,
        role_client: TestClient,
        grant: Grants,
        classroom_a: Classroom,
        classroom_a2: Classroom,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ])

        assert (
            role_client.get(f"/classrooms/{classroom_a2.id}").status_code == FORBIDDEN
        )

    def test_update_with_classroom_update(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ, ClassroomAction.UPDATE])
        body = _classroom_body(building_a)

        response = role_client.put(f"/classrooms/{classroom_a.id}", json=body)

        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json()["name"] == body["name"]

    def test_update_is_refused_with_read_only(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        classroom_a: Classroom,
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.READ])

        response = role_client.put(
            f"/classrooms/{classroom_a.id}", json=_classroom_body(building_a)
        )

        assert response.status_code == FORBIDDEN

    def test_delete_with_classroom_delete(
        self, role_client: TestClient, grant: Grants, classroom_a: Classroom
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.DELETE])

        response = role_client.delete(f"/classrooms/{classroom_a.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT, response.text

    def test_delete_is_refused_with_update_only(
        self, role_client: TestClient, grant: Grants, classroom_a: Classroom
    ) -> None:
        grant.classroom(classroom_a, [ClassroomAction.UPDATE])

        assert (
            role_client.delete(f"/classrooms/{classroom_a.id}").status_code == FORBIDDEN
        )


class TestSubjects:
    def test_create_with_building_create(
        self, role_client: TestClient, grant: Grants, building_a: Building
    ) -> None:
        grant.building(building_a, [BuildingAction.CREATE])
        body = SubjectRequestFactory(building_ids=[must_be_int(building_a.id)])

        response = role_client.post(
            "/subjects", json=jsonable_encoder(body.create_input())
        )

        assert response.status_code == status.HTTP_200_OK, response.text

    def test_create_is_refused_on_another_building(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        building_b: Building,
    ) -> None:
        grant.building(building_a, [BuildingAction.CREATE])
        body = SubjectRequestFactory(building_ids=[must_be_int(building_b.id)])

        response = role_client.post(
            "/subjects", json=jsonable_encoder(body.create_input())
        )

        assert response.status_code == FORBIDDEN

    def test_read_with_building_read(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_a: Subject,
        subject_b: Subject,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])

        assert role_client.get(f"/subjects/{subject_a.id}").status_code == 200
        assert role_client.get(f"/subjects/{subject_b.id}").status_code == FORBIDDEN

    def test_update_with_building_update(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_a: Subject,
    ) -> None:
        grant.building(building_a, [BuildingAction.UPDATE])
        body = SubjectRequestFactory(building_ids=[must_be_int(building_a.id)])

        response = role_client.put(
            f"/subjects/{subject_a.id}", json=jsonable_encoder(body.update_input())
        )

        assert response.status_code == status.HTTP_200_OK, response.text

    def test_update_is_refused_with_read_only(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_a: Subject,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])
        body = SubjectRequestFactory(building_ids=[must_be_int(building_a.id)])

        response = role_client.put(
            f"/subjects/{subject_a.id}", json=jsonable_encoder(body.update_input())
        )

        assert response.status_code == FORBIDDEN

    def test_delete_takes_update(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_a: Subject,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])
        assert role_client.delete(f"/subjects/{subject_a.id}").status_code == FORBIDDEN

        grant.building(building_a, [BuildingAction.UPDATE])
        response = role_client.delete(f"/subjects/{subject_a.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT, response.text

    def test_building_delete_implies_update(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_a: Subject,
    ) -> None:
        # DELETE implies UPDATE (and READ): deleting without editing makes no
        # sense, so it also deletes subjects, which take UPDATE.
        grant.building(building_a, [BuildingAction.DELETE])

        response = role_client.delete(f"/subjects/{subject_a.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT, response.text


class TestSubjectRecrawl:
    """PATCH /subjects/crawl overwrites subjects with JupiterWeb data: UPDATE
    on each subject's building (the crawl itself is mocked)."""

    @staticmethod
    def _recrawl(client: TestClient, *codes: str) -> tuple[int, AsyncMock]:
        crawl = AsyncMock(
            return_value=SubjectCrawlResponse(
                update=True, codes=list(codes), failed=[], sucess=list(codes), errors=[]
            )
        )
        with patch.object(SubjectRepository, "crawler_update_many", crawl):
            response = client.patch(
                "/subjects/crawl",
                json={"subject_codes": list(codes), "type": CrawlerType.JUPITER},
            )
        return response.status_code, crawl

    def test_with_building_update(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_a: Subject,
    ) -> None:
        grant.building(building_a, [BuildingAction.UPDATE])

        status_code, crawl = self._recrawl(role_client, subject_a.code)

        assert status_code == status.HTTP_200_OK
        crawl.assert_awaited_once()

    def test_refused_with_read_only(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_a: Subject,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])

        status_code, crawl = self._recrawl(role_client, subject_a.code)

        assert status_code == FORBIDDEN
        crawl.assert_not_awaited()

    def test_one_subject_of_another_building_refuses_all(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_a: Subject,
        subject_b: Subject,
    ) -> None:
        grant.building(building_a, [BuildingAction.UPDATE])

        status_code, crawl = self._recrawl(role_client, subject_a.code, subject_b.code)

        assert status_code == FORBIDDEN
        crawl.assert_not_awaited()

    def test_an_unknown_code_is_left_to_the_crawl(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_a: Subject,
    ) -> None:
        # Reported per subject by the crawl, as before.
        grant.building(building_a, [BuildingAction.UPDATE])

        status_code, crawl = self._recrawl(role_client, subject_a.code, "XXX0000")

        assert status_code == status.HTTP_200_OK
        crawl.assert_awaited_once()


class TestClasses:
    def test_create_with_building_create(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_a: Subject,
    ) -> None:
        grant.building(building_a, [BuildingAction.CREATE])
        body = jsonable_encoder(ClassRequestFactory(subject_a).create_input())

        response = role_client.post("/classes", json=body)

        assert response.status_code == status.HTTP_200_OK, response.text

    def test_create_is_refused_on_another_building(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_b: Subject,
    ) -> None:
        grant.building(building_a, [BuildingAction.CREATE])
        body = jsonable_encoder(ClassRequestFactory(subject_b).create_input())

        assert role_client.post("/classes", json=body).status_code == FORBIDDEN

    def test_read_with_building_read(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        class_a: Class,
        class_b: Class,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])

        assert role_client.get(f"/classes/{class_a.id}").status_code == 200
        assert role_client.get(f"/classes/{class_b.id}").status_code == FORBIDDEN

    def test_update_with_building_update(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_a: Subject,
        class_a: Class,
    ) -> None:
        grant.building(building_a, [BuildingAction.UPDATE])
        body = jsonable_encoder(ClassRequestFactory(subject_a).update_input())

        response = role_client.put(f"/classes/{class_a.id}", json=body)

        assert response.status_code == status.HTTP_200_OK, response.text

    def test_update_is_refused_with_read_only(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        subject_a: Subject,
        class_a: Class,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])
        body = jsonable_encoder(ClassRequestFactory(subject_a).update_input())

        assert (
            role_client.put(f"/classes/{class_a.id}", json=body).status_code
            == FORBIDDEN
        )

    def test_delete_takes_update(
        self,
        role_client: TestClient,
        grant: Grants,
        building_a: Building,
        class_a: Class,
    ) -> None:
        grant.building(building_a, [BuildingAction.READ])
        assert role_client.delete(f"/classes/{class_a.id}").status_code == FORBIDDEN

        grant.building(building_a, [BuildingAction.UPDATE])
        response = role_client.delete(f"/classes/{class_a.id}")
        assert response.status_code in (200, 204), response.text
