from typing import Unpack

from sqlmodel import Session

from server.models.database.classroom_db_model import Classroom
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.schedule_db_model import Schedule
from server.models.dicts.database.occurrence_database_dicts import OccurrenceModelDict
from server.utils.must_be_int import must_be_int
from tests.factories.base.occurrence_base_factory import OccurrenceBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class OccurrenceModelFactory(BaseModelFactory[Occurrence]):
    def __init__(
        self, schedule: Schedule, session: Session, classroom: Classroom | None = None
    ) -> None:
        super().__init__(session)
        self.schedule = schedule
        self.classroom = classroom
        self.core_factory = OccurrenceBaseFactory()

    def _get_model_type(self) -> type[Occurrence]:
        return Occurrence

    def get_defaults(self) -> OccurrenceModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "schedule_id": must_be_int(self.schedule.id),
            "schedule": self.schedule,
            "classroom_id": must_be_int(self.classroom.id) if self.classroom else None,
            "classroom": self.classroom,
            "occurrence_label": None,
        }

    def create(self, **overrides: Unpack[OccurrenceModelDict]) -> Occurrence:  # type: ignore
        """Create an occurrence instance with default values."""
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[OccurrenceModelDict]
    ) -> Occurrence:
        """Create an occurrence instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, occurrence_id: int, **overrides: Unpack[OccurrenceModelDict]
    ) -> Occurrence:
        """Update an occurrence instance with default values."""
        return super().update(model_id=occurrence_id, **overrides)
