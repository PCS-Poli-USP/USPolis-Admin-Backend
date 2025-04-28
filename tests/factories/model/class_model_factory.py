from datetime import date, datetime, timedelta
from typing import Unpack
from sqlmodel import Session
from server.models.database.class_db_model import Class
from server.models.database.subject_db_model import Subject
from server.models.dicts.database.class_database_dicts import ClassModelDict
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.class_type import ClassType
from tests.factories.model.base_model_factory import BaseModelFactory


class ClassModelFactory(BaseModelFactory[Class]):
    def __init__(self, subject: Subject, session: Session) -> None:
        super().__init__(session)
        self.subject = subject

    def _get_model_type(self) -> type[Class]:
        return Class

    def get_defaults(self) -> ClassModelDict:
        return {
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=30),
            "code": self.faker.numerify(text="%%%%%%%"),
            "professors": [self.faker.name()],
            "type": self.faker.random_element(ClassType.values()),
            "vacancies": self.faker.random_int(min=1, max=100),
            "air_conditionating": self.faker.boolean(),
            "accessibility": self.faker.boolean(),
            "audiovisual": self.faker.random_element(AudiovisualType.values()),
            "ignore_to_allocate": self.faker.boolean(),
            "full_allocated": False,
            "updated_at": datetime.now(),
            "calendars": [],
            "schedules": [],
            "subject": self.subject,
            "posts": [],
        }

    def create(self, **overrides: Unpack[ClassModelDict]) -> Class:  # type: ignore
        """Create a class instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: Unpack[ClassModelDict]) -> Class:  # type: ignore
        """Create a class instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(self, class_id: int, **overrides: Unpack[ClassModelDict]) -> Class:  # type: ignore
        """Create a class instance with default values."""
        return super().update(model_id=class_id, **overrides)
