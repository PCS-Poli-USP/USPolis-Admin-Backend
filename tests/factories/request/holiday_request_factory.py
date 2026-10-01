from datetime import datetime
from typing import Unpack

from server.models.database.holiday_category_db_model import HolidayCategory
from server.models.dicts.requests.holiday_requests_dicts import (
    HolidayManyRegisterDict,
    HolidayRegisterDict,
    HolidayUpdateDict,
)
from server.models.http.requests.holiday_request_models import (
    HolidayManyRegister,
    HolidayRegister,
    HolidayUpdate,
)
from server.utils.must_be_int import must_be_int
from tests.factories.base.holiday_base_factory import HolidayBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory


class HolidayRequestFactory(BaseRequestFactory):
    def __init__(self, category: HolidayCategory) -> None:
        super().__init__()
        self.category = category
        self.core_factory = HolidayBaseFactory(must_be_int(category.id))
        self.faker = self.core_factory.faker

    def get_default_create(self) -> HolidayRegisterDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "date": self.faker.date_time_between(
                start_date=datetime.now(), end_date="+300d"
            ),
        }

    def get_default_update(self) -> HolidayUpdateDict:
        return self.get_default_create()

    def get_default_create_many(self) -> HolidayManyRegisterDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "dates": [
                self.faker.date_time_between(
                    start_date=datetime.now(), end_date="+300d"
                )
                for _ in range(3)
            ],
        }

    def create_input(self, **overrides: Unpack[HolidayRegisterDict]) -> HolidayRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return HolidayRegister(**default)

    def update_input(self, **overrides: Unpack[HolidayUpdateDict]) -> HolidayUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return HolidayUpdate(**default)

    def create_many_input(
        self, **overrides: Unpack[HolidayManyRegisterDict]
    ) -> HolidayManyRegister:
        default = self.get_default_create_many()
        self.override_default_dict(default, overrides)  # type: ignore
        return HolidayManyRegister(**default)
