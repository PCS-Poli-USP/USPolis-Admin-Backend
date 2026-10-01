from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.user_db_model import User
from tests.utils.curriculum_test_utils import make_curriculum

URL_PREFIX = "/curriculums"


class TestGetAllCurriculums:
    def test_returns_all_curriculums(
        self, public_client: TestClient, admin_user: User, session: Session
    ) -> None:
        curriculum = make_curriculum(admin_user=admin_user, session=session)

        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        matches = [c for c in response.json() if c["id"] == curriculum.id]
        assert len(matches) == 1
        assert matches[0]["description"] == "Grade 2024"
        assert matches[0]["course"] == "Ciência da Computação"
