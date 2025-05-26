from typing import Unpack

from server.models.dicts.requests.user_requests_dicts import (
    UserRegisterDict,
    UserUpdateDict,
)
from server.models.http.requests.user_request_models import UserRegister, UserUpdate
from tests.factories.base.user_base_factory import UserBaseFactory
from tests.factories.request.base_request_factory import BaseRequestFactory


class UserRequestFactory(BaseRequestFactory):
    def __init__(self) -> None:
        super().__init__()
        self.core_factory = UserBaseFactory()

    def get_default_create(self) -> UserRegisterDict:
        """Get default values for creating a UserRegister."""
        core = self.core_factory.get_register_defaults()
        return {**core}

    def create_input(self, **overrides: Unpack[UserRegisterDict]) -> UserRegister:
        default = self.get_default_create()
        self.override_default_dict(default, overrides)  # type: ignore
        return UserRegister(**default)

    def update_input(self, **overrides: Unpack[UserUpdateDict]) -> UserUpdate:
        default = self.core_factory.get_update_defaults()
        self.override_default_dict(default, overrides)  # type: ignore
        return UserUpdate(**default)
