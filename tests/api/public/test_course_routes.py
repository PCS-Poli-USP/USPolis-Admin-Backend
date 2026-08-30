from unittest.mock import AsyncMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.course_options_db_model import CourseOptions
from server.models.database.user_db_model import User
from server.repositories.course_options_repository import CourseOptionRepository
from server.services.jupiter_crawler.course_models import CourseOption
from tests.factories.model.course_model_factory import CourseModelFactory

URL_PREFIX = "/courses"


class TestGetAllCourses:
    def test_returns_all_courses(
        self, public_client: TestClient, admin_user: User, session: Session
    ) -> None:
        course = CourseModelFactory(
            creator=admin_user, session=session
        ).create_and_refresh(name="Ciência da Computação")

        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        matches = [c for c in response.json() if c["id"] == course.id]
        assert len(matches) == 1
        assert matches[0]["name"] == "Ciência da Computação"


class TestListInactiveCourses:
    def test_returns_courses_from_the_crawler(self, public_client: TestClient) -> None:
        with patch(
            "server.routes.public.course_routes.JupiterCoursesOldCrawler.crawl",
            new=AsyncMock(
                return_value=[CourseOption(codcur=1, codhab=2, name="Curso Antigo")]
            ),
        ):
            response = public_client.get(f"{URL_PREFIX}/jupiter/inactive-courses")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{"codcur": 1, "codhab": 2, "name": "Curso Antigo"}]


class TestListActiveCourses:
    def test_returns_courses_from_the_crawler(self, public_client: TestClient) -> None:
        with patch(
            "server.routes.public.course_routes.JupiterCoursesCrawler.crawl",
            new=AsyncMock(
                return_value=[CourseOption(codcur=3, codhab=4, name="Curso Ativo")]
            ),
        ):
            response = public_client.get(f"{URL_PREFIX}/jupiter/active-courses")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{"codcur": 3, "codhab": 4, "name": "Curso Ativo"}]


class TestListCachedCourseOptions:
    def test_returns_previously_synced_options(
        self, public_client: TestClient, session: Session
    ) -> None:
        CourseOptionRepository(session).upsert_many(
            [CourseOptions(codcur=10, codhab=20, name="Estatística")]
        )

        response = public_client.get(f"{URL_PREFIX}/options")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{"codcur": 10, "codhab": 20, "name": "Estatística"}]

    def test_returns_empty_when_nothing_was_synced_yet(
        self, public_client: TestClient
    ) -> None:
        response = public_client.get(f"{URL_PREFIX}/options")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestSyncCourseOptions:
    def test_crawls_and_persists_active_and_inactive_options(
        self, public_client: TestClient, session: Session
    ) -> None:
        with (
            patch(
                "server.routes.public.course_routes.JupiterCoursesCrawler.crawl",
                new=AsyncMock(
                    return_value=[CourseOption(codcur=1, codhab=1, name="Ativo")]
                ),
            ),
            patch(
                "server.routes.public.course_routes.JupiterCoursesOldCrawler.crawl",
                new=AsyncMock(
                    return_value=[CourseOption(codcur=2, codhab=2, name="Inativo")]
                ),
            ),
        ):
            response = public_client.post(f"{URL_PREFIX}/options/sync")

        assert response.status_code == status.HTTP_200_OK
        names = {o["name"] for o in response.json()}
        assert names == {"Ativo", "Inativo"}
        assert {o.name for o in CourseOptionRepository(session).list_all()} == {
            "Ativo",
            "Inativo",
        }
