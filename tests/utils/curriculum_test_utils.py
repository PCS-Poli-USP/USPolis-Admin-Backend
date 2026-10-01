"""Shared, DB-backed helper for creating Course/Curriculum rows in tests -
keep every such helper here instead of redeclaring local make_curriculum
functions per test file.

This persists (unlike academic_test_utils.py/time_test_utils.py's DB-free
build() helpers) because it backs integration/route-level tests that need a
real, queryable row - so it delegates to CourseModelFactory/
CurriculumModelFactory's create_and_refresh() rather than .build(). See
TESTS.md's "Test data protocol" section for when to use which."""

from typing import Any

from sqlmodel import Session

from server.models.database.curriculum_db_model import Curriculum
from server.models.database.user_db_model import User
from tests.factories.model.course_model_factory import CourseModelFactory
from tests.factories.model.curriculum_model_factory import CurriculumModelFactory


def _given(**kwargs: Any) -> dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


def make_curriculum(
    *,
    admin_user: User,
    session: Session,
    course_name: str = "Ciência da Computação",
    codcur: int | None = None,
    codhab: int | None = None,
    description: str = "Grade 2024",
) -> Curriculum:
    course = CourseModelFactory(creator=admin_user, session=session).create_and_refresh(
        name=course_name
    )
    return CurriculumModelFactory(
        course=course, creator=admin_user, session=session
    ).create_and_refresh(description=description, **_given(codcur=codcur, codhab=codhab))
