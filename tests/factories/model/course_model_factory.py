from datetime import datetime
from typing import Unpack

from sqlmodel import Session

from server.models.database.course_db_model import Course
from server.models.database.user_db_model import User
from server.models.dicts.database.course_database_dicts import CourseModelDict
from server.utils.must_be_int import must_be_int
from tests.factories.base.course_base_factory import CourseBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class CourseModelFactory(BaseModelFactory[Course]):
    def __init__(self, creator: User, session: Session) -> None:
        super().__init__(session)
        self.creator = creator
        self.core_factory = CourseBaseFactory()

    def _get_model_type(self) -> type[Course]:
        return Course

    def get_defaults(self) -> CourseModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "created_at": datetime.now(),
            "created_by_id": must_be_int(self.creator.id),
            "updated_at": datetime.now(),
            "updated_by_id": must_be_int(self.creator.id),
            "curriculums": [],
        }

    def create(self, **overrides: Unpack[CourseModelDict]) -> Course:  # type: ignore
        """Create a course instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: Unpack[CourseModelDict]) -> Course:  # type: ignore
        """Create a course instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(self, course_id: int, **overrides: Unpack[CourseModelDict]) -> Course:  # type: ignore
        """Update a course instance with default values."""
        return super().update(model_id=course_id, **overrides)
