from datetime import datetime
from typing import Unpack

from sqlmodel import Session

from server.models.database.course_db_model import Course
from server.models.database.curriculum_db_model import Curriculum
from server.models.database.user_db_model import User
from server.models.dicts.database.curriculum_database_dicts import CurriculumModelDict
from server.utils.must_be_int import must_be_int
from tests.factories.base.curriculum_base_factory import CurriculumBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class CurriculumModelFactory(BaseModelFactory[Curriculum]):
    def __init__(self, course: Course, creator: User, session: Session) -> None:
        super().__init__(session)
        self.course = course
        self.creator = creator
        self.core_factory = CurriculumBaseFactory()

    def _get_model_type(self) -> type[Curriculum]:
        return Curriculum

    def get_defaults(self) -> CurriculumModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "course_id": must_be_int(self.course.id),
            "course": self.course,
            "created_at": datetime.now(),
            "created_by_id": must_be_int(self.creator.id),
            "updated_at": datetime.now(),
            "updated_by_id": must_be_int(self.creator.id),
            "subjects": [],
            "users": [],
        }

    def create(self, **overrides: Unpack[CurriculumModelDict]) -> Curriculum:  # type: ignore
        """Create a curriculum instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[CurriculumModelDict]
    ) -> Curriculum:
        """Create a curriculum instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, curriculum_id: int, **overrides: Unpack[CurriculumModelDict]
    ) -> Curriculum:
        """Update a curriculum instance with default values."""
        return super().update(model_id=curriculum_id, **overrides)
