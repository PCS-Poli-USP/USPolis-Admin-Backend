from typing import Unpack, cast
from server.models.dicts.requests.subject_requests_dicts import (
    SubjectRegisterDict,
    SubjectUpdateDict,
)
from server.models.http.requests.subject_request_models import (
    SubjectRegister,
    SubjectUpdate,
)
from tests.factories.base.subject_base_factory import SubjectBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory


class SubjectRequestFactory(BaseRequestFactory):
    def __init__(self, building_ids: list[int]) -> None:
        super().__init__()
        self.building_ids = building_ids
        self.core_factory = SubjectBaseFactory()

    def get_default_create(self) -> SubjectRegisterDict:
        """Get default values for creating a SubjectRegister."""
        core = self.core_factory.get_base_defaults()
        return cast(
            SubjectRegisterDict,
            {
                "building_ids": self.building_ids,
                **core,
            },
        )

    def create_input(self, **overrides: Unpack[SubjectRegisterDict]) -> SubjectRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return SubjectRegister(**default)

    def update_input(self, **overrides: Unpack[SubjectUpdateDict]) -> SubjectUpdate:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return SubjectUpdate(**default)
