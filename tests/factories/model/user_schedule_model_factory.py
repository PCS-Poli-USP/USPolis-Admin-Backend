from datetime import datetime
from typing import Unpack

from sqlmodel import Session

from server.models.database.user_db_model import User
from server.models.database.user_schedule_db_model import UserSchedule
from server.models.dicts.database.user_schedule_database_dicts import (
    UserScheduleModelDict,
)
from server.utils.must_be_int import must_be_int
from tests.factories.base.user_schedule_base_factory import UserScheduleBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class UserScheduleModelFactory(BaseModelFactory[UserSchedule]):
    def __init__(self, user: User, session: Session) -> None:
        super().__init__(session)
        self.user = user
        self.core_factory = UserScheduleBaseFactory()

    def _get_model_type(self) -> type[UserSchedule]:
        return UserSchedule

    def get_defaults(self) -> UserScheduleModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "user_id": must_be_int(self.user.id),
            "user": self.user,
            "entries": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    def create(self, **overrides: Unpack[UserScheduleModelDict]) -> UserSchedule:  # type: ignore
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[UserScheduleModelDict]
    ) -> UserSchedule:
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, user_schedule_id: int, **overrides: Unpack[UserScheduleModelDict]
    ) -> UserSchedule:
        return super().update(model_id=user_schedule_id, **overrides)
