from typing import Unpack
from sqlmodel import Session
from server.models.database.class_db_model import Class
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.dicts.database.schedule_database_dicts import ScheduleModelDict
from server.utils.enums.week_day import WeekDay
from tests.factories.base.schedule_base_factory import ScheduleBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class ScheduleModelFactory(BaseModelFactory[Schedule]):
    def __init__(
        self, class_: Class | None, reservation: Reservation | None, session: Session
    ) -> None:
        super().__init__(session)
        if class_ is None and reservation is None:
            raise ValueError("Either class_ or reservation must be provided.")

        self.core_factory = ScheduleBaseFactory()
        self.class_ = class_
        self.reservation = reservation

    def _get_model_type(self) -> type[Schedule]:
        return Schedule

    def get_defaults(self) -> ScheduleModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "week_day": self.core_factory.faker.random_element(WeekDay.workdays()),
            "month_week": None,
            "class_id": self.class_.id if self.class_ else None,
            "reservation_id": self.reservation.id if self.reservation else None,
            "classroom_id": None,
            "class_": self.class_,
            "reservation": self.reservation,
            "classroom": None,
            "occurrences": [],
            "logs": [],
        }

    def create(self, **overrides: Unpack[ScheduleModelDict]) -> Schedule:  # type: ignore
        return super().create(**overrides)

    def create_and_refresh(self, **overrides: Unpack[ScheduleModelDict]) -> Schedule:  # type: ignore
        """Create a schedule instance with default values, commit and refresh it."""
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, schedule_id: int, **overrides: Unpack[ScheduleModelDict]
    ) -> Schedule:
        """Create a schedule instance with default values."""
        return super().update(model_id=schedule_id, **overrides)
