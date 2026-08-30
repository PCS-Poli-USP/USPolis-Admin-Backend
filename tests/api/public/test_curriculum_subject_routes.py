from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from server.models.database.curriculum_db_model import Curriculum
from server.models.database.curriculum_subject_db_model import CurriculumSubject
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.utils.enums.curriculum_subject_category_enum import (
    CurriculumSubjectCategory,
)
from server.utils.enums.curriculum_subject_type_enum import CurriculumSubjectType
from server.utils.must_be_int import must_be_int
from tests.utils.curriculum_test_utils import make_curriculum

URL_PREFIX = "/curriculum_subjects"


def make_curriculum_subject(
    *, curriculum: Curriculum, subject: Subject, session: Session, period: int = 1
) -> CurriculumSubject:
    curriculum_subject = CurriculumSubject(
        curriculum_id=must_be_int(curriculum.id),
        subject_id=must_be_int(subject.id),
        type=CurriculumSubjectType.SEMESTRAL,
        category=CurriculumSubjectCategory.MANDATORY,
        period=period,
    )
    session.add(curriculum_subject)
    session.commit()
    session.refresh(curriculum_subject)
    return curriculum_subject


class TestGetSubjectsByCurriculum:
    def test_returns_subjects_for_the_given_curriculum(
        self,
        public_client: TestClient,
        admin_user: User,
        subject: Subject,
        session: Session,
    ) -> None:
        curriculum = make_curriculum(admin_user=admin_user, session=session)
        curriculum_subject = make_curriculum_subject(
            curriculum=curriculum, subject=subject, session=session
        )

        response = public_client.get(f"{URL_PREFIX}/{curriculum.id}/subjects")

        assert response.status_code == status.HTTP_200_OK
        matches = [cs for cs in response.json() if cs["id"] == curriculum_subject.id]
        assert len(matches) == 1
        assert matches[0]["subject"]["code"] == subject.code

    def test_returns_empty_for_a_curriculum_with_no_subjects(
        self, public_client: TestClient, admin_user: User, session: Session
    ) -> None:
        curriculum = make_curriculum(admin_user=admin_user, session=session)

        response = public_client.get(f"{URL_PREFIX}/{curriculum.id}/subjects")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestGetAllCurriculumSubjects:
    def test_returns_all_curriculum_subjects(
        self,
        public_client: TestClient,
        admin_user: User,
        subject: Subject,
        session: Session,
    ) -> None:
        curriculum = make_curriculum(admin_user=admin_user, session=session)
        curriculum_subject = make_curriculum_subject(
            curriculum=curriculum, subject=subject, session=session
        )

        response = public_client.get(URL_PREFIX)

        assert response.status_code == status.HTTP_200_OK
        assert curriculum_subject.id in [cs["id"] for cs in response.json()]
