from datetime import datetime
from typing import Unpack
from sqlmodel import Session
from server.models.database.class_db_model import Class
from server.models.database.subject_db_model import Subject
from server.models.dicts.database.class_database_dicts import ClassModelDict
from tests.factories.base.class_base_factory import ClassBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory
from tests.factories.model.schedule_model_factory import ScheduleModelFactory


class ClassModelFactory(BaseModelFactory[Class]):
    def __init__(self, subject: Subject, session: Session) -> None:
        super().__init__(session)
        self.subject = subject
        self.core_factory = ClassBaseFactory()

    def _get_model_type(self) -> type[Class]:
        return Class

    def get_defaults(self) -> ClassModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "full_allocated": False,
            "updated_at": datetime.now(),
            "calendars": [],
            "schedules": [],
            "subject": self.subject,
            "posts": [],
        }

    def create(self, **overrides: Unpack[ClassModelDict]) -> Class:  # type: ignore
        """Create a class instance with default values.\n
        A default class has a single schedule.\n
        """
        class_ = super().create(**overrides)
        if overrides.get("schedules") is None:
            factory = ScheduleModelFactory(
                class_=class_, reservation=None, session=self.session
            )
            factory.create()
        return class_

    def create_and_refresh(self, **overrides: Unpack[ClassModelDict]) -> Class:  # type: ignore
        """Create a class instance with default values, commit and refresh it."""
        class_ = self.create(**overrides)
        self.session.commit()
        self.session.refresh(class_)
        return class_

    def update(self, class_id: int, **overrides: Unpack[ClassModelDict]) -> Class:  # type: ignore
        """Create a class instance with default values."""
        return super().update(model_id=class_id, **overrides)
