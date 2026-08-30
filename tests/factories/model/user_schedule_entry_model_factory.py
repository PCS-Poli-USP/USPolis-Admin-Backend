from datetime import datetime
from typing import Unpack

from sqlmodel import Session

from server.models.database.schedule_db_model import Schedule
from server.models.database.user_schedule_db_model import UserSchedule
from server.models.database.user_schedule_entry_db_model import UserScheduleEntry
from server.models.dicts.database.user_schedule_entry_database_dicts import (
    UserScheduleEntryModelDict,
)
from server.utils.must_be_int import must_be_int
from tests.factories.base.user_schedule_entry_base_factory import (
    UserScheduleEntryBaseFactory,
)
from tests.factories.model.base_model_factory import BaseModelFactory


class UserScheduleEntryModelFactory(BaseModelFactory[UserScheduleEntry]):
    def __init__(
        self, user_schedule: UserSchedule, schedule: Schedule, session: Session
    ) -> None:
        super().__init__(session)
        self.user_schedule = user_schedule
        self.schedule = schedule
        self.core_factory = UserScheduleEntryBaseFactory()

    def _get_model_type(self) -> type[UserScheduleEntry]:
        return UserScheduleEntry

    def get_defaults(self) -> UserScheduleEntryModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "user_schedule_id": must_be_int(self.user_schedule.id),
            "schedule_id": must_be_int(self.schedule.id),
            "user_schedule": self.user_schedule,
            "schedule": self.schedule,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    def create(  # type: ignore
        self, **overrides: Unpack[UserScheduleEntryModelDict]
    ) -> UserScheduleEntry:
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[UserScheduleEntryModelDict]
    ) -> UserScheduleEntry:
        return super().create_and_refresh(**overrides)
