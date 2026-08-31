from datetime import datetime
from typing import Unpack

from sqlmodel import Session

from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.database.holiday_db_model import Holiday
from server.models.database.user_db_model import User
from server.models.dicts.database.holiday_database_dicts import HolidayModelDict
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.must_be_int import must_be_int
from tests.factories.base.holiday_base_factory import HolidayBaseFactory
from tests.factories.model.base_model_factory import BaseModelFactory


class HolidayModelFactory(BaseModelFactory[Holiday]):
    def __init__(
        self, creator: User, category: HolidayCategory, session: Session
    ) -> None:
        super().__init__(session)
        self.creator = creator
        self.category = category
        self.core_factory = HolidayBaseFactory(must_be_int(category.id))

    def _get_model_type(self) -> type[Holiday]:
        return Holiday

    def get_defaults(self) -> HolidayModelDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "date": self.core_factory.faker.date_between(
                start_date="today", end_date="+300d"
            ),
            "updated_at": datetime.now(),
            "category": self.category,
            "created_by_id": must_be_int(self.creator.id),
            "created_by": self.creator,
        }

    def create(self, **overrides: Unpack[HolidayModelDict]) -> Holiday:  # type: ignore
        return super().create(**overrides)

    def create_and_refresh(  # type: ignore
        self, **overrides: Unpack[HolidayModelDict]
    ) -> Holiday:
        return super().create_and_refresh(**overrides)

    def update(  # type: ignore
        self, holiday_id: int, **overrides: Unpack[HolidayModelDict]
    ) -> Holiday:
        holiday = super().update(model_id=holiday_id, **overrides)
        holiday.updated_at = BrazilDatetime.now_utc()
        return holiday
