from unittest.mock import AsyncMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.repositories.course_options_repository import CourseOptionRepository
from server.services.jupiter_crawler.course_models import CourseOption

SYNC_URL = "/admin/courses/options/sync"
ROUTES = "server.routes.admin.course_admin_routes"


class TestSyncCourseOptions:
    def test_crawls_and_persists_active_and_inactive_options(
        self, client: TestClient, session: Session
    ) -> None:
        with (
            patch(
                f"{ROUTES}.JupiterCoursesCrawler.crawl",
                new=AsyncMock(
                    return_value=[CourseOption(codcur=1, codhab=1, name="Ativo")]
                ),
            ),
            patch(
                f"{ROUTES}.JupiterCoursesOldCrawler.crawl",
                new=AsyncMock(
                    return_value=[CourseOption(codcur=2, codhab=2, name="Inativo")]
                ),
            ),
        ):
            response = client.post(SYNC_URL)

        assert response.status_code == status.HTTP_200_OK
        names = {o["name"] for o in response.json()}
        assert names == {"Ativo", "Inativo"}
        assert {o.name for o in CourseOptionRepository(session).list_all()} == {
            "Ativo",
            "Inativo",
        }

    def test_non_admins_cannot_trigger_crawls(
        self, restricted_client: TestClient
    ) -> None:
        with patch(f"{ROUTES}.JupiterCoursesCrawler.crawl", new=AsyncMock()) as crawl:
            response = restricted_client.post(SYNC_URL)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        crawl.assert_not_called()

    def test_the_old_public_route_is_gone(self, public_client: TestClient) -> None:
        response = public_client.post("/courses/options/sync")

        assert response.status_code in (
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
