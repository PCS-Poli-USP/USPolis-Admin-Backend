from typing import Unpack

from server.models.dicts.requests.calendar_requests_dicts import (
    CalendarRegisterDict,
    CalendarUpdateDict,
)
from server.models.http.requests.calendar_request_models import (
    CalendarRegister,
    CalendarUpdate,
)
from tests.factories.base.calendar_base_factory import CalendarBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory


class CalendarRequestFactory(BaseRequestFactory):
    def __init__(self, categories_ids: list[int] | None = None) -> None:
        super().__init__()
        self.categories_ids = categories_ids
        self.core_factory = CalendarBaseFactory()

    def get_default_create(self) -> CalendarRegisterDict:
        core = self.core_factory.get_base_defaults()
        return {
            **core,
            "categories_ids": self.categories_ids,
        }

    def get_default_update(self) -> CalendarUpdateDict:
        return self.get_default_create()

    def create_input(self, **overrides: Unpack[CalendarRegisterDict]) -> CalendarRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return CalendarRegister(**default)

    def update_input(self, **overrides: Unpack[CalendarUpdateDict]) -> CalendarUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return CalendarUpdate(**default)
