from typing import Unpack

from server.models.dicts.requests.user_requests_dicts import (
    UserRegisterDict,
    UserUpdateDict,
)
from server.models.http.requests.user_request_models import UserRegister, UserUpdate
from tests.factories.request.base_request_factory import BaseRequestFactory


class UserRequestFactory(BaseRequestFactory):
    def create_input(self, **overrides: Unpack[UserRegisterDict]) -> UserRegister:
        default: UserRegisterDict = {
            "is_admin": False,
            "building_ids": [],
            "name": self.faker.name(),
            "email": self.random_email(),
        }
        self.override_default_dict(default, overrides)  # type: ignore
        return UserRegister(**default)

    def update_input(self, **overrides: Unpack[UserUpdateDict]) -> UserUpdate:
        default: UserUpdateDict = {
            "is_admin": False,
            "building_ids": [],
        }
        self.override_default_dict(default, overrides)  # type: ignore
        return UserUpdate(**default)
