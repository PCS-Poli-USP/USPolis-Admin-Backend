from typing import Unpack

from sqlmodel import Session

from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.user_db_model import User
from server.models.dicts.database.holiday_category_database_dicts import (
    HolidayCategoryModelDict,
)
from server.utils.must_be_int import must_be_int
from tests.factories.base.holiday_category_base_factory import (
    HolidayCategoryBaseFactory,
)
from tests.factories.model.base_model_factory import BaseModelFactory


class HolidayCategoryModelFactory(BaseModelFactory[HolidayCategory]):
    def __init__(self, creator: User, session: Session) -> None:
        super().__init__(session)
        self.creator = creator
        self.core_factory = HolidayCategoryBaseFactory()

    def _get_model_type(self) -> type[HolidayCategory]:
        return HolidayCategory

    def get_defaults(self) -> HolidayCategoryModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "created_by_id": must_be_int(self.creator.id),
            "created_by": self.creator,
            "holidays": [],
            "calendars": [],
        }

    def create(  # type: ignore
        self, **overrides: Unpack[HolidayCategoryModelDict]
    ) -> HolidayCategory:
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[HolidayCategoryModelDict]
    ) -> HolidayCategory:
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, holiday_category_id: int, **overrides: Unpack[HolidayCategoryModelDict]
    ) -> HolidayCategory:
        return super().update(model_id=holiday_category_id, **overrides)
