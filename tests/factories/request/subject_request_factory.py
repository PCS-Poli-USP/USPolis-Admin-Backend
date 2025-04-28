from typing import Unpack
from server.models.dicts.requests.subject_requests_dicts import (
    SubjectRegisterDict,
    SubjectUpdateDict,
)
from server.utils.enums.subject_type import SubjectType
from tests.factories.request.base_request_factory import BaseRequestFactory


class SubjectRequestFactory(BaseRequestFactory):
    def __init__(self, building_ids: list[int]) -> None:
        super().__init__()
        self.building_ids = building_ids

    def get_default_create(self) -> SubjectRegisterDict:
        """Get default values for creating a SubjectRegister."""
        return {
            "building_ids": self.building_ids,
            "name": self.faker.name(),
            "code": self.faker.bothify(text="???%%%%", letters=self.LETTERS),
            "professors": [self.faker.name()],
            "type": self.faker.random_element(SubjectType.values()),
            "class_credit": self.faker.random_int(min=1, max=10),
            "work_credit": self.faker.random_int(min=1, max=10),
        }

    def create_input(
        self, **overrides: Unpack[SubjectRegisterDict]
    ) -> SubjectRegisterDict:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return default

    def update_input(self, **overrides: Unpack[SubjectUpdateDict]) -> SubjectUpdateDict:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return default
