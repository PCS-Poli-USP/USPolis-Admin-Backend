from server.models.dicts.base.user_base_dict import UserBaseDict
from server.models.dicts.requests.user_requests_dicts import (
    UserRegisterDict,
    UserUpdateDict,
)
from tests.factories.base.base_factory import BaseFactory


class UserBaseFactory(BaseFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_random_email(self) -> str:
        """Generate a random email address."""
        return self.faker.email(domain="usp.br")

    def get_random_name(self) -> str:
        """Generate a random name."""
        return self.faker.name()

    def get_base_defaults(self) -> UserBaseDict:
        return {
            "is_admin": False,
        }

    def get_update_defaults(self) -> UserUpdateDict:
        return {
            "is_admin": False,
            "group_ids": None,
        }

    def get_register_defaults(self) -> UserRegisterDict:
        return {
            "name": self.faker.name(),
            "email": self.faker.email(domain="usp.br"),
            "is_admin": False,
            "group_ids": None,
        }
