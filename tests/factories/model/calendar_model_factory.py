from typing import Unpack

from sqlmodel import Session

from server.models.database.calendar_db_model import Calendar
from server.models.database.user_db_model import User
from server.models.dicts.database.calendar_database_dicts import CalendarModelDict
from server.utils.must_be_int import must_be_int
from tests.factories.base.calendar_base_factory import CalendarBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class CalendarModelFactory(BaseModelFactory[Calendar]):
    def __init__(self, creator: User, session: Session) -> None:
        super().__init__(session)
        self.creator = creator
        self.core_factory = CalendarBaseFactory()

    def _get_model_type(self) -> type[Calendar]:
        return Calendar

    def get_defaults(self) -> CalendarModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "created_by_id": must_be_int(self.creator.id),
            "created_by": self.creator,
            "categories": [],
            "classes": [],
        }

    def create(self, **overrides: Unpack[CalendarModelDict]) -> Calendar:  # type: ignore
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: Unpack[CalendarModelDict]) -> Calendar:  # type: ignore
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, calendar_id: int, **overrides: Unpack[CalendarModelDict]
    ) -> Calendar:
        return super().update(model_id=calendar_id, **overrides)
