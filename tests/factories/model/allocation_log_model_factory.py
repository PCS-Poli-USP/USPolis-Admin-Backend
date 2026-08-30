from datetime import datetime
from typing import Unpack

from sqlmodel import Session

from server.models.database.allocation_log_db_model import AllocationLog
from server.models.database.schedule_db_model import Schedule
from server.models.dicts.database.allocation_log_database_dicts import (
    AllocationLogModelDict,
)
from server.utils.must_be_int import must_be_int
from tests.factories.base.allocation_log_base_factory import AllocationLogBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class AllocationLogModelFactory(BaseModelFactory[AllocationLog]):
    def __init__(self, schedule: Schedule, session: Session) -> None:
        super().__init__(session)
        self.schedule = schedule
        self.core_factory = AllocationLogBaseFactory()

    def _get_model_type(self) -> type[AllocationLog]:
        return AllocationLog

    def get_defaults(self) -> AllocationLogModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "modified_at": datetime.now(),
            "schedule_id": must_be_int(self.schedule.id),
            "schedule": self.schedule,
        }

    def create(self, **overrides: Unpack[AllocationLogModelDict]) -> AllocationLog:  # type: ignore
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[AllocationLogModelDict]
    ) -> AllocationLog:
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, allocation_log_id: int, **overrides: Unpack[AllocationLogModelDict]
    ) -> AllocationLog:
        return super().update(model_id=allocation_log_id, **overrides)
