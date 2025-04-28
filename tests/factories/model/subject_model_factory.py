from typing import Unpack
from sqlmodel import Session
from server.models.database.building_db_model import Building

from server.models.database.subject_db_model import Subject
from server.models.dicts.database.subject_database_dicts import SubjectModelDict
from server.utils.enums.subject_type import SubjectType
from tests.factories.model.base_model_factory import BaseModelFactory


class SubjectModelFactory(BaseModelFactory[Subject]):
    def __init__(self, building: Building, session: Session) -> None:
        super().__init__(session)
        self.building = building

    def _get_model_type(self) -> type[Subject]:
        return Subject

    def get_defaults(self) -> SubjectModelDict:
        return {
            "name": self.faker.name(),
            "code": self.faker.bothify(text="???%%%%", letters=self.LETTERS),
            "professors": [self.faker.name()],
            "type": self.faker.random_element(SubjectType.values()),
            "class_credit": self.faker.random_int(min=1, max=10),
            "work_credit": self.faker.random_int(min=1, max=10),
            "buildings": [self.building],
            "classes": [],
            "forum": None,
        }

    def create(self, **overrides: Unpack[SubjectModelDict]) -> Subject:  # type: ignore
        """Create a class instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: Unpack[SubjectModelDict]) -> Subject:  # type: ignore
        """Create a class instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(self, subject_id: int, **overrides: Unpack[SubjectModelDict]) -> Subject:  # type: ignore
        """Create a class instance with default values."""
        return super().update(model_id=subject_id, **overrides)
