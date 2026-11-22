from typing import Unpack

from server.models.dicts.requests.institutional_event_requests_dicts import (
    InstitutionalEventRegisterDict,
    InstitutionalEventUpdateDict,
)
from server.models.http.requests.institutional_event_request_models import (
    InstitutionalEventRegister,
    InstitutionalEventUpdate,
)
from tests.factories.base.institutional_event_base_factory import (
    InstitutionalEventBaseFactory,
)
from tests.factories.request.base_request_factory import BaseRequestFactory


class InstitutionalEventRequestFactory(BaseRequestFactory):
    def __init__(self) -> None:
        super().__init__()
        self.core_factory = InstitutionalEventBaseFactory()

    def get_default_create(self) -> InstitutionalEventRegisterDict:
        return {**self.core_factory.get_base_defaults()}

    def get_default_update(self) -> InstitutionalEventUpdateDict:
        return self.get_default_create()

    def create_input(
        self, **overrides: Unpack[InstitutionalEventRegisterDict]
    ) -> InstitutionalEventRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return InstitutionalEventRegister(**default)

    def update_input(
        self, **overrides: Unpack[InstitutionalEventUpdateDict]
    ) -> InstitutionalEventUpdate:
        default = self.get_default_update()
        self.override_default_dict(default, overrides)  # type: ignore
        return InstitutionalEventUpdate(**default)
