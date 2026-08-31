from typing import Unpack

from server.models.dicts.requests.holiday_category_requests_dicts import (
    HolidayCategoryRegisterDict,
    HolidayCategoryUpdateDict,
)
from server.models.http.requests.holiday_category_request_models import (
    HolidayCategoryRegister,
    HolidayCategoryUpdate,
)
from tests.factories.base.holiday_category_base_factory import (
    HolidayCategoryBaseFactory,
)
from tests.factories.request.base_request_factory import BaseRequestFactory


class HolidayCategoryRequestFactory(BaseRequestFactory):
    def __init__(self) -> None:
        super().__init__()
        self.core_factory = HolidayCategoryBaseFactory()

    def get_default_create(self) -> HolidayCategoryRegisterDict:
        return self.core_factory.get_base_defaults()

    def get_default_update(self) -> HolidayCategoryUpdateDict:
        return self.get_default_create()

    def create_input(
        self, **overrides: Unpack[HolidayCategoryRegisterDict]
    ) -> HolidayCategoryRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return HolidayCategoryRegister(**default)

    def update_input(
        self, **overrides: Unpack[HolidayCategoryUpdateDict]
    ) -> HolidayCategoryUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return HolidayCategoryUpdate(**default)
